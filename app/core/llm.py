import os
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv


load_dotenv()

MISTRAL_API_KEY =os.getenv("MISTRAL_API_KEY")
_llm = None

def get_llm():
    global _llm
    
    if _llm is None:
        _llm = ChatMistralAI(
            model="mistral-small-latest",
            api_key=MISTRAL_API_KEY,
            temperature=0
        )
    return _llm