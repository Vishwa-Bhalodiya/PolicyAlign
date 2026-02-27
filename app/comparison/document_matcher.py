from sqlalchemy.orm import Session
from typing import Dict, List
from collections import defaultdict

from app.models.paragraph import Paragraph
from app.comparison.semantic_matcher import (match_client_paragraph, build_vendor_vector_store)
from app.comparison.gap_analyzer import analyze_gaps
from app.comparison.vector_store import DomainVectorStore
from app.ingestion.atomic_splitter import split_into_atomic


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
    
    vendor_paragraphs = (
        db.query(Paragraph)
        .filter(Paragraph.document_id == vendor_document_id)
        .all()
    )
    
    vendor_texts = [v.text for v in vendor_paragraphs]
    total_paragraphs = len(client_paragraphs)
    
    all_vendor_atomics = []
    paragraph_ids = []
    domains = []
    
    pid_counter = 0
    
    for vendor_text in vendor_texts:
        vendor_atomics = split_into_atomic(vendor_text)
        
        for v_atomic in vendor_atomics:
            all_vendor_atomics.append(v_atomic)
            paragraph_ids.append(pid_counter)
            domains.append("Vendor")
            pid_counter += 1
            
    atomic_vector_store = DomainVectorStore()
    atomic_vector_store.build(all_vendor_atomics, paragraph_ids, domains)
    
    matched : List[Dict] = []
    unmatched : List[str] = []
    confidence_scores: List[float] = []
    
    #Track how many times each vendor paragraph is reused
    vendor_match_counter = defaultdict(int)
    
    
    for para in client_paragraphs:
        result = match_client_paragraph(db, para.id, vector_store)
        
        if not result or not result.get("matched_vendor_paragraphs"):
            
            atomic_matched, atomic_gaps = analyze_gaps(para.text, atomic_vector_store, vendor_texts)
            
            
            print("Atomic Matched:", atomic_matched)
            print("Atomic Gaps:", atomic_gaps)
            #Add atomic matches
            for m in atomic_matched:
                matched.append({
                    "client_paragraph": m["client_atomic"],
                    "confidence": m["confidence"],
                    "atomic_level": True
                })
                confidence_scores.append(m["confidence"])
                
            #Track atomic gaps separately
            for g in atomic_gaps:
                unmatched.append(g)
            
            continue
        
        best_match = result["matched_vendor_paragraphs"][0]
        vendor_id = best_match["paragraph_id"]
        
        vendor_match_counter[vendor_id] +=1
        
        if vendor_match_counter[vendor_id] >5:
            penalty = 0.05*(vendor_match_counter[vendor_id] - 5)
            best_match["final_score"] = max (
                0.0,
                round(best_match["final_score"] - penalty, 3)
            )
            
            
        confidence = best_match["final_score"]
        confidence_scores.append(confidence)
        
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