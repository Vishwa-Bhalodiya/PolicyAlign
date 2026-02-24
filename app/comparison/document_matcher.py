from sqlalchemy.orm import Session
from typing import Dict, List

from app.models.paragraph import Paragraph
from app.comparison.semantic_matcher import (match_client_paragraph, build_vendor_vector_store)


def match_documents(db: Session, client_document_id: int, vendor_document_id: int) -> Dict:
    
    vector_store = build_vendor_vector_store(db, vendor_document_id)
    
    if not vector_store or not vector_store.vector_store:
        return {
            "matched": [],
            "unmatched_client_paragraphs": [],
            "document_summary": {
                "coverage_percentage": 0.0,
                "average_confidence": 0.0,
                "total_client_paragraphs": 0,
                "matched_count": 0
            }
        }
        
    
    client_paragraphs = (
        db.query(Paragraph)
        .filter(Paragraph.document_id == client_document_id)
        .all()
    )
    
    total_paragraphs = len(client_paragraphs)
    
    matched : List[Dict] = []
    unmatched : List[str] = []
    
    confidence_scores: List[float] = []
    
    
    for para in client_paragraphs:
        result = match_client_paragraph(db, para.id, vector_store)
        
        if not result or not result["matched_vendor_paragraphs"]:
            unmatched.append(para.text)
            continue
        
        best_match = result["matched_vendor_paragraphs"][0]
        
        confidence_scores.append(result["confidence"])
        
        matched.append({
            "client_paragraph": para.text,
            "client_domain": result["domain"],
            "vendor_paragraph_id": best_match["paragraph_id"],
            "vendor_paragraph": best_match["text"],
            "vendor_domain": best_match["domain"],
            "embedding_score": best_match["embedding_score"],
            "ai_score": best_match["ai_score"],
            "final_score": best_match["final_score"],
            "confidence": result["confidence"],
            "reason": best_match["reason"]
        })
        
    matched_count = len(matched)
    
    coverage = (
        (matched_count / total_paragraphs)*100
        if total_paragraphs > 0 else 0.0
    )
    
    average_confidence = (
        sum(confidence_scores) / len(confidence_scores)
        if confidence_scores else 0.0
    )
            
    return{
        "matched": matched,
        "unmatched_client_paragraphs": unmatched,
        "document_summary": {
            "total_client_paragraphs": total_paragraphs,
            "matched_count" : matched_count,
            "coverage_percentage": round(coverage, 2),
            "average_confidence": round(average_confidence, 3)
        } 
    }