import pdfplumber
import fitz # PyMuPDF
from docx import Document
import re
import os


def clean_text(text: str) -> str:
    
    text = re.sub(r"[\t]+", " ", text)#Remove multiple spaces
    text = re.sub(r"\n{3,}", "\n\n", text)#Remove excessive line breaks
    text = re.sub(r"Page\s+\d+\s+of\s+\d+", "", text, flags=re.IGNORECASE)#Remove page numbers like: "Page 1 of 20"
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)#Remove standalone page numbers
    text = text.strip()#Strip leading/trailing whitespace
    
    return text
    

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("pdfplumber failed:", e)
    
    if not text.strip():
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text("text")
        except Exception as e:
            print("PyMuPDF fallback failed:", e)
            
    if not text.strip():
        raise ValueError("unable to extract text from PDF.")
            
    return clean_text(text)



def extract_text_from_docx(file_path: str) -> str:
    
    try:
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        raise ValueError(f"DOCX extraction failed: {e}")
    
    return clean_text(text)

def extract_text(file_path: str, filename: str) -> str:
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    filename = filename.lower()
    
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_path)
    
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
    