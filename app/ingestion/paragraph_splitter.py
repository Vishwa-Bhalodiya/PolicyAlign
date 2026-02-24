import uuid
from typing import List
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.utils.pdf_cleanup import normalize, looks_like_metadata, detect_repeated_lines

MIN_PARAGRAPH_LENGTH = 20 #characters

#Define Structured Output
class ParagraphList(BaseModel):
    paragraphs: List[str] = Field(
        description="List of logically separated paragraphs"
    )
    
parser = PydanticOutputParser(pydantic_object=ParagraphList)

#Initialize Mistral
llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0,
    timeout=180
)

#Create Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a senior legal and compliance expert.

Your task is to split the given policy document into logically separated paragraphs based on compliance meaning.

STRICT RULES:

1. Each paragraph must represent ONE complete compliance obligation.
2. If multiple distinct obligations exist, split them.
3. Preserve original wording exactly.
4. Do NOT invent content.
5. Return ONLY valid JSON.

OUTPUT FORMAT:
{{
    "paragraphs": ["text1", "text2"]
}}
"""
        ),
        (
            "user",
            """
Document:

{document}

{format_instructions}
"""
        ),
    ]
)

chain = prompt | llm | parser

#Main Function

def split_into_paragraphs(text: str):

    text = text.replace("\r\n", "\n").replace("\r","\n")
    lines = text.split("\n")
    
    repeated_lines = detect_repeated_lines(lines)
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if normalize(stripped) in repeated_lines and looks_like_metadata(stripped):
            continue
        
        if stripped:
            cleaned_lines.append(stripped)
            
    cleaned_text = "\n".join(cleaned_lines)
    
    if len(cleaned_text) >12000:
        cleaned_text = cleaned_text[:12000]
    
    #AI-based semantic splitting
    try:
        result = chain.invoke(
            {
                "document": cleaned_text,
                "format_instructions": parser.get_format_instructions(),
            }
        )
        paragraphs = result.paragraphs
        
    except Exception as e:
        print("AI splitting failed:", e)
        paragraphs = cleaned_text.split(r'\n(?=\d+\.)')
    
    return [
        {
            "paragraph_id": str(uuid.uuid4()),
            "text": p.strip(),
        }
        for p in paragraphs
        if len(p.strip()) >= MIN_PARAGRAPH_LENGTH
    ]