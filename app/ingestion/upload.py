import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from app.ingestion.extractor import extract_text
from app.ingestion.paragraph_splitter import split_into_paragraphs
from app.ingestion.paragraph_service import sav_paragraphs
from app.db.database import SessionLocal
from app.models.documents import Document

#from app.classification.domain_classifier import classify_paragraphs

router = APIRouter(
    prefix="/upload",
    tags=["Document Upload"]
)

UPLOAD_DIR = "uploaded_files"
MAX_FILE_SIZE_MB = 50
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_document(file_path: str, filename: str, document_id: int):
    db = SessionLocal()
    
    try:
        extracted_text = extract_text(file_path, filename)
        
        paragraphs = split_into_paragraphs(extracted_text)
        
        sav_paragraphs(
            db=db,
            document_id=document_id,
            paragraphs=paragraphs,
        )
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print("Background processing failed:", e)
        
    finally:
        db.close()
        
        

@router.post("/upload-policy/")
async def upload_policy(background_tasks: BackgroundTasks, document_type: str, file: UploadFile = File(...)):
    
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX allowed.")
    
    contents = await file.read()
    
    if len(contents) > MAX_FILE_SIZE_MB*1024*1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max {MAX_FILE_SIZE_MB} MB allowed."
        )
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(contents)
        
    db = SessionLocal()
        
    try:
        db_document = Document(
            filename=file.filename,
            file_path=file_path,
            document_id=file_id,
            document_type=document_type,
            status="processing"
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        background_tasks.add_task(
            process_document,
            file_path,
            file.filename,
            db_document.id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Document creation failed: {str(e)}"
        )
        
    finally:
        db.close()
        
    return {
        "file_id": file_id,
        "filename": file.filename,
        "message": "File uploaded. Processing started."
    }
