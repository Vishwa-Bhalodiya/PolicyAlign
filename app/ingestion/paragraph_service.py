from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.paragraph import Paragraph
from app.models.paragraph_classification import ParagraphClassification
from app.models.domains import ComplianceDomain
from app.classification.domain_classifier import classify_paragraph


def sav_paragraphs(db: Session, document_id: int, paragraphs: list):
    
    try:
        for para in paragraphs:

            # Save paragraph
            paragraph_obj = Paragraph(
                paragraph_id=para["paragraph_id"],
                document_id=document_id,
                text=para["text"]
            )

            db.add(paragraph_obj)
            db.flush() #generates paragraph_obj.id

            # Classify paragraph
            result = classify_paragraph(para["text"], db)

            domain_name = result.get("domain")
            confidence = result.get("confidence", 0.0)
            method = result.get("method", "unknown")
            
            # Fetch domain from DB
            domain = (
                db.query(ComplianceDomain)
                .filter(ComplianceDomain.name == domain_name)
                .first()
            )
            
            if not domain:
                classification = ParagraphClassification(
                    paragraph_id=paragraph_obj.id,
                    domain_id=None,
                    confidence=confidence,
                    method="invalid-domain"
                )
            else:
                classification = ParagraphClassification(
                    paragraph_id=paragraph_obj.id,
                    domain_id=domain.id,
                    confidence=confidence,
                    method=method
                )

            db.add(classification)
        db.commit()
            
    except SQLAlchemyError as e:
        db.rollback()
        raise e
