import numpy as np
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session


from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


from app.models.domains import ComplianceDomain


#Load embedding model
model = SentenceTransformer("all-mpnet-base-v2")

EMBEDDING_THRESHOLD = 0.60
AI_THRESHOLD = 0.70


#Domain Cache (Avoid recomputing embeddings)
_domain_cache = {
    "names": None,
    "embeddings": None
}

#Load Domains from Database

def load_domains_from_db(db: Session) -> Tuple[List[str], np.ndarray]:
    
    global _domain_cache
    
    if _domain_cache["names"] is not None:
        return _domain_cache["names"], _domain_cache["embeddings"]
    
    domains = db.query(ComplianceDomain).all()
    
    if not domains:
        raise ValueError("No domains found in database.")
    
    names = [d.name for d in domains]
    descriptions = [d.description for d in domains]
    
    embeddings = model.encode(
        descriptions,
        normalize_embeddings=True
    )
    
    _domain_cache["names"] = names
    _domain_cache["embeddings"] = embeddings
    
    return names, embeddings
    
    
#Rule-Based Keywords

RULE_KEYWORDS = {
    "Data Protection & Privacy": ["data protection", "privacy", "personal data", "data subject", "consent", "gdpr"],
    "Information Security": ["information security", "confidentiality", "integrity", "availability", "cybersecurity", "threats"],
    "Access Control & Identity Management": ["access control", "identity management", "authentication", "authorization", "iam"],
    "Data Retention & Deletion": ["data retention", "data deletion", "data lifecycle", "retention schedule", "secure deletion"],
    "Incident Response & Breach Management": ["incident response", "breach management", "security incident", "incident detection", "incident reporting"],
    "Compliance & Regulatory Obligations": ["compliance", "regulatory obligations", "laws and regulations", "compliance standards"],
    "Risk Management": ["risk management", "risk assessment", "risk mitigation", "risk acceptance"],
    "Audit & Monitoring": ["audit", "monitoring", "logging", "compliance reviews"],
    "Business Continuity & Disaster Recovery": ["business continuity", "disaster recovery", "continuity planning", "backups", "disaster recovery processes"],
    "Third-Party & Vendor Management": ["third-party management", "vendor management", "vendor risk management", "third-party compliance controls"],
    "Operational Security": ["operational security", "operational procedures", "secure system usage"]
}

def rule_based_classification(paragraph: str, valid_domains: List[str]) -> Dict:
    
    text = paragraph.lower()
    
    for domain, keywords in RULE_KEYWORDS.items():
        if domain not in valid_domains:
            continue
        
        for keyword in keywords:
            if keyword in text:
                return {
                    "domain": domain,
                    "confidence": 0.92,
                    "method": "rule-based"
                }
    return{}

#AI STRUCTURED OUTPUT
class DomainPrediction(BaseModel):
    domain: str = Field(description="Best matching compliance domain")
    confidence: float = Field(description="Confidence score between 0 and 1")
    
parser = PydanticOutputParser(pydantic_object=DomainPrediction)

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0
)


def ai_classify(paragraph: str, valid_domains: List[str]) -> Dict:
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
                You must classify the paragraph into EXACTLY ONE domain from this list:
                
                {valid_domains}
                
                Return ONLY valid JSON:
                
                {{
                    "domain": "<exact name>",
                    "confidence": <float>
                }}
                """
            ),
            (
                "user",
                "{paragraph}"
            )
        ]
    )
    
    chain = prompt| llm | parser
    
    try:
        result = chain.invoke({"paragraph": paragraph})
        
        if result.domain in valid_domains:
            return {
                "domain": result.domain,
                "confidence": round(result.confidence, 3),
                "method": "ai-based"
            }
            
    except Exception:
        pass
    
    return {}


#Single Paragraph Classification

def classify_paragraph(paragraph: str, db: Session)-> Dict:
    
    valid_domains, domain_embeddings = load_domains_from_db(db)
    
    #Rule-based first
    rule_result = rule_based_classification(paragraph, valid_domains)
    
    if rule_result:
        return rule_result
    
    #Embeddingd-based
    paragraph_embedding = model.encode(
        [paragraph],
        normalize_embeddings=True
    )
    
    similarities = cosine_similarity(
        paragraph_embedding,
        domain_embeddings
    )[0]
    
    best_index = int(np.argmax(similarities))
    best_score = float(similarities[best_index])
    predicted_domain = valid_domains[best_index]
    
    if best_score >= EMBEDDING_THRESHOLD:
        return {
            "domain": predicted_domain,
            "confidence": round(best_score, 3),
            "method": "embedding-based"
        }
        
    
    #AI Fallback Only If Ambiguous
    ai_result = ai_classify(paragraph, valid_domains)
    
    if ai_result and ai_result["confidence"] >= AI_THRESHOLD:
        return ai_result
    
    
    #Lowest Similarity Domain (No fake label)
    return {
        "domain": predicted_domain,
        "confidence": round(best_score, 3),
        "method": "low-confidence"
    }
    
        
#Batch Classification
def classify_paragraphs(paragraphs: List[Dict], db: Session) -> List[Dict]:
    
    results =[]
    
    for para in paragraphs:
        result = classify_paragraph(para["text"], db)
        
        results.append({
            "paragraph_id": para["paragraph_id"],
            "domain": result["domain"],
            "confidence": result["confidence"],
            "method": result["method"]
        })
        
    return results