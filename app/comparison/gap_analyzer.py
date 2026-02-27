from typing import List, Dict
from app.ingestion.atomic_splitter import split_into_atomic
from app.comparison.atomic_matcher import atomic_ai_match
from app.comparison.remediation import suggest_remediation
from app.comparison.vector_store import DomainVectorStore

STRICT_THRESHOLD = 0.65
AI_CALL_THRESHOLD = 0.80
TOP_K = 2

def analyze_gaps(client_paragraph: str,  vector_store: DomainVectorStore, vendor_paragraphs: List[str]):

    matched = []
    gaps = []

    atomics = split_into_atomic(client_paragraph)       

    for atomic in atomics:

        best_result = None
        best_candidate_text = None
        best_embedding_score = 0.0
        
        candidates = vector_store.search(
            query_text=atomic,
            domain=None,
            top_k=TOP_K
        )
        
        for candidate in candidates:
            embedding_score = candidate["score"]
            
            if embedding_score > best_embedding_score:
                best_embedding_score = embedding_score
                best_candidate_text = candidate["text"]
            
            if embedding_score < AI_CALL_THRESHOLD:
                continue
            
            result = atomic_ai_match(atomic, candidate["text"])
    
    
            if not result:
                continue

            if not best_result or result.similarity_score > best_result.similarity_score:
                best_result = result
                
            if result.match and result.similarity_score >= 0.80:
                break
            
        is_gap = (
            not best_result or not best_result.match or best_result.similarity_score < STRICT_THRESHOLD
        )
        
        if is_gap:
            vendor_sample = (
                vendor_paragraphs[0]
                if vendor_paragraphs 
                else "No vendor text available"
            )
            
            suggestion = suggest_remediation(atomic, vendor_sample)
            
            gaps.append({
                "client_atomic": atomic,
                "gap_type": (
                    best_result.gap_type 
                    if best_result 
                    else "Completely absent obligation"
                ),
                "reason": (
                    best_result.reason 
                    if best_result 
                    else "No substantial match found."
                ),
                "suggested_vendor_text": suggestion,
                "closet_vendor_text": best_candidate_text,
                "closet_embedding_score": round(best_embedding_score, 3),
                "ai_similarity_score": round(best_result.similarity_score, 3) if best_result else None
            })
        else:   
            matched.append({
                "client_atomic": atomic,
                "confidence": best_result.similarity_score
            })

    return matched, gaps