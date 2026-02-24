from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db.database import Base
from sqlalchemy.orm import relationship
from app.models.paragraph_classification import ParagraphClassification

class Paragraph(Base):
    __tablename__ = "paragraphs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    paragraph_id = Column(String(50), unique=True, index=True)
    
    text = Column(Text, nullable=False)
    
    document = relationship("Document", back_populates="paragraphs", passive_deletes=True)
    
    classification = relationship(
    "ParagraphClassification",
    back_populates="paragraph",
    uselist=False,
    cascade="all, delete-orphan",
    passive_deletes=True
)

    
    