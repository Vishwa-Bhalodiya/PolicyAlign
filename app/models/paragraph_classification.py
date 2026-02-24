from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class ParagraphClassification(Base):
    __tablename__ = "paragraph_classifications"

    id = Column(Integer, primary_key=True, index=True)

    paragraph_id = Column(Integer, ForeignKey("paragraphs.id", ondelete="CASCADE"), nullable=False)
    
    domain_id = Column(Integer, ForeignKey("compliance_domains.id",ondelete="SET NULL"), nullable=True)

    confidence = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)

    paragraph = relationship("Paragraph", back_populates="classification", passive_deletes=True)
    
    
    domain = relationship("ComplianceDomain", passive_deletes=True)
