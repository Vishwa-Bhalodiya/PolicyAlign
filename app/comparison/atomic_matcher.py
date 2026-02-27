from pydantic import BaseModel, Field
from typing import Optional, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.core.llm import get_llm
import time
import random
from langchain_mistralai import ChatMistralAI
from app.core.rate_limiter import rate_limiter

llm = get_llm()

AI_MATCH_CACHE: Dict[str, "AtomicMatchResult"] = {}

class AtomicMatchResult(BaseModel):
    match: bool
    similarity_score: float
    gap_type: Optional[str]
    reason: Optional[str]

parser = PydanticOutputParser(pydantic_object=AtomicMatchResult)

MATCH_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Compare client clause and vendor clause.

            Determine:
            - match (true/false)
            - similarity_score (0-1)
            - gap_type if mismatch:
                - Missing scope
                - Missing enforcement
                - Missing implementation detail
                - Missing regulatory reference
                - Vague language
                - Completely absent obligation
            - reason (short explanation)

            If match=false, clearly explain what is missing.
            Return strict JSON.
            """
        ),
        (
            "user",
            """
            CLIENT:
            {client}

            VENDOR:
            {vendor}
            """
        )
    ]
)

chain = MATCH_PROMPT | llm | parser

def atomic_ai_match(client_atomic: str, vendor_candidate: str):
    cache_key = f"{client_atomic.strip()} || {vendor_candidate.strip()}"
    
    if cache_key in AI_MATCH_CACHE:
        return AI_MATCH_CACHE[cache_key]
    
    max_retries = 3
    
    for attempt in range(max_retries):
        
        try:
            rate_limiter.wait()  # Ensure we respect rate limits
            result = chain.invoke({
                "client": client_atomic,
                "vendor": vendor_candidate
            })
            
            AI_MATCH_CACHE[cache_key] = result
            return result
        
        except Exception as e:
            
            if "429" in str(e):
                wait_time = 5*(attempt + 1)
                print(f"Rate limit hit. Waiting {wait_time} seconds ...")
                time.sleep(wait_time)
            else:
                break
    return None