from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.core.llm import get_llm
from app.core.rate_limiter import rate_limiter

llm = get_llm()

ALLOWED_TYPES = [
    "Obligation",
    "Prohibition",
    "Enforcement",
    "Regulatory requirement",
    "coditional obligation",
    "Informational",
    "Scope",
    "Heading",
    "Metadata",
    "Form field"
]

class AtomicClassification(BaseModel):
    category: str = Field(description="Compliance category")

parser = PydanticOutputParser(pydantic_object=AtomicClassification)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Classify the sentence into ONE category:

            - Obligation
            - Prohibition
            - Conditional obligation
            - Informational
            - Scope
            - Enforcement
            - Regulatory requirement
            - Heading
            - Metadata
            - Form field

            Return valid JSON:
            {
              "category": "..."
            }
            """
        ),
        ("user", "{sentence}")
    ]
)

chain = prompt | llm | parser

def classify_atomic(sentence: str):
    try:
        rate_limiter.wait()  # Ensure we respect rate limits
        result = chain.invoke({"sentence": sentence})
        if result.category in ALLOWED_TYPES:
            return result.category
        return None
    except:
        return None