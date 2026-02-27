import json
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

from app.models.paragraph import Paragraph
from app.models.paragraph_classification import ParagraphClassification
from app.comparison.vector_store import DomainVectorStore
from app.core.rate_limiter import rate_limiter



llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}}
)

embedding_model = SentenceTransformer("all-mpnet-base-v2")



def ai_semantic_match(client_text: str, vendor_text: str)-> Dict :
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
    """
    You are a senior legal, regulatory, and compliance expert.
    
    Determine whether the vendor paragraph SUBSTANTIALLY satisfies the compliance obligation stated in the client paragraph.
    
    Substantial satisfaction requires:
    
    - Equivalent scope
    - Equivalent regulatory refrence (if mentioned)
    - Equivalent implementation obligation
    - Equivalent enforcement requirement
    
    General governance language does NOT qualify.
    Broader but vague language does NOT qualify.
    If explicit requirements are missing, return match=false.
    
    Minor wording differences do NOT invalidate equivalence.
    
    
    Be objective and conservative in judgment.
    
    Return STRICT JSON only:
    
    {{
        "match": true or false,
        "similarity_score" : number between 0 to 1,
        "reason" : "Short precise explanation"
    }}
    """
            ),
            (
                "user",
    """
    Client Paragraph:
    {client_text}
    
    Vendor Paragraph:
    {vendor_text}
    
    Determine whether the vendor paragraph substantially satisfies the compliance obligation of the client paragraph.
    """
            )
        ]
    )
    
    chain = prompt | llm
    rate_limiter.wait()  # Ensure we respect rate limits
    result =  chain.invoke({
        "client_text": client_text,
        "vendor_text": vendor_text
    })
    
    
    try:
        return json.loads(result.content)
    except Exception:
        return{
            "match": False,
            "similarity_score": 0.0,
            "reason": "Invalid AI response"
        }



def build_vendor_vector_store(db: Session, vendor_document_id: int) -> DomainVectorStore:

    vendor_paragraphs = (
        db.query(Paragraph)
        .filter(Paragraph.document_id == vendor_document_id, Paragraph.document.has(document_type = "vendor")).all()
    )

    texts = []
    paragraph_ids = []
    domains = []
    
    
    for para in vendor_paragraphs:
        classification = (
            db.query(ParagraphClassification)
            .filter(ParagraphClassification.paragraph_id == para.id)
            .first()
        )

        if classification:
            texts.append(para.text)
            paragraph_ids.append(para.id)
            domains.append(classification.domain.name)

    vector_store = DomainVectorStore()
    vector_store.build(texts, paragraph_ids, domains)

    return vector_store


def match_client_paragraph(db: Session, client_paragraph_id: int, vector_store: DomainVectorStore,top_k_domain: int=2, top_k_global: int = 1) -> Optional[Dict]:

    client_para = db.query(Paragraph).filter(Paragraph.id == client_paragraph_id).first()
    
    if not client_para:
        return None

    classification = (
        db.query(ParagraphClassification)
        .filter(ParagraphClassification.paragraph_id == client_paragraph_id)
        .first()
    )
    
    domain_name = classification.domain.name if classification else None

    domain_matches = vector_store.search(
        client_para.text,
        domain_name,
        top_k=top_k_domain
    ) if domain_name else []
    
    
    global_matches = vector_store.search(
        client_para.text,
        None,
        top_k=top_k_global
    )
    
    combined = {}
    for m in domain_matches + global_matches:
        combined[m["paragraph_id"]] = m
        
    candidates = list(combined.values())
    
    if not candidates:
        return{
            "client_paragraph": client_para.text,
            "domain": domain_name,
            "confidence": 0.0,
            "matched_vendor_paragraphs": []
        }
    

    verified_matches = []
    
    EMBEDDING_THRESHOLD = 0.50
    
    for candidate in candidates:
        embedding_score = candidate.get("score", 0.0)
        
        if embedding_score < EMBEDDING_THRESHOLD:
            continue
        
        ai_result = ai_semantic_match(
            client_para.text,
            candidate["text"]
        )
        
        ai_score = ai_result.get("similarity_score", 0.0)
        
        final_score = (embedding_score * 0.3) + (ai_score * 0.7)

        if domain_name and candidate["domain"] != domain_name:
            final_score = max(0.0, final_score - 0.05)
        
        if ai_result.get("match") and final_score >=0.60:
            verified_matches.append({
                "paragraph_id": candidate["paragraph_id"],
                "text": candidate["text"],
                "domain": candidate["domain"],
                "embedding_score": round(embedding_score, 3),
                "ai_score": round(ai_score, 3),
                "final_score": round(final_score, 3),
                "reason": ai_result.get("reason", "")
            })
   
   
    verified_matches.sort(key=lambda x: x["final_score"], reverse=True)
    
    confidence = verified_matches[0]["final_score"] if verified_matches else 0.0
    
    return{
        "client_paragraph": client_para.text,
        "domain": domain_name,
        "confidence": round(confidence, 3),
        "matched_vendor_paragraphs": verified_matches
    }