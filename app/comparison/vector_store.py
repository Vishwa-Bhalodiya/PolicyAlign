from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List, Optional, Dict
import numpy as np

class DomainVectorStore:

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        self.vector_store: Optional[FAISS] = None
        
    def build(self, texts: List[str], paragraph_ids: List[int], domains: List[str]):
        
        documents = []
        
        for text, pid, domain in zip(texts, paragraph_ids, domains):
            documents.append(
                Document(
                    page_content = text,
                    metadata={
                        "paragraph_id": pid,
                        "domain": domain
                    }
                )
            )
            
        if not documents:
            self.vector_store = None
            return
            
        self.vector_store = FAISS.from_documents(
            documents,
            self.embeddings
        )
        
    @staticmethod
    def _distance_to_similarity(distance: float) -> float:
        """
        Converts FAISS L2 distance to a bounded similarity score(0-1).
        
        """
        similarity = 1 / (1 + distance)
        return float(similarity)
    
        
    def search(self, query_text:str, domain: Optional[str] = None, top_k: int=5) -> List[Dict]:
        
        if not self.vector_store:
            return []
        
        raw_results = self.vector_store.similarity_search_with_score(
            query_text,
            k=top_k*5
        )
        
        candidates = []
        
        for doc, distance in raw_results:
            
            similarity = self._distance_to_similarity(distance)
            
            domain_match = (
                1.05 if domain and doc.metadata.get("domain") == domain
                else 1.0
            )
            
            boosted_score = similarity * domain_match

            candidates.append({
                "paragraph_id": doc.metadata.get("paragraph_id"),
                "text": doc.page_content,
                "domain": doc.metadata.get("domain"),
                "score": round(min(boosted_score, 1.0), 4)
            })
                
        candidates.sort(key=lambda x: x["score"], reverse=True)
            
        return candidates[:top_k]