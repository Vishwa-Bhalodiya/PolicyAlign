from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
print("MISTRAL_API_KEY:", os.getenv("MISTRAL_API_KEY"))
#Register all models before app starts
import app.models.documents
import app.models.paragraph
import app.models.paragraph_classification
import app.models.domains

from app.db.database import SessionLocal
from app.comparison.document_matcher import match_documents
from app.ingestion.upload import router as ingestion_router
from app.comparison.gap_analyzer import analyze_gaps


app = FastAPI(title="PolicyAlign - Policy Compliance System")

# Include ingestion routes
app.include_router(ingestion_router, prefix="/api")


#DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Document-Level Matching API
@app.get("/api/document-matching/")
def document_matching(
    client_document_id: int,
    vendor_document_id: int,
    db: Session = Depends(get_db)
):
    return match_documents(db, client_document_id, vendor_document_id)
