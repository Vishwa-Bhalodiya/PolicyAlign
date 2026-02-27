from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.comparison.gap_analyzer import analyze_gaps
from app.comparison.report_builder import build_report

router = APIRouter()

class ComparisonRequest(BaseModel):
    client_paragraph: str
    vendor_paragraphs: List[str]
    
@router.post("/analyze")
def analyze_compliance(request: ComparisonRequest):
    
    matched, gaps = analyze_gaps(
        request.client_paragraph, 
        request.vendor_paragraphs
    )
    
    return build_report(matched, gaps)
    