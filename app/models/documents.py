from sqlalchemy import Column, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    document_id = Column(String(50), unique=True, index=True)
    
    filename = Column(String(255), nullable=False)
    
    file_path = Column(String(255), nullable=False)
    
    document_type = Column(String(50), nullable=False)
    status = Column(String(50), default="processing")
    
    paragraphs = relationship(
        "Paragraph",
        back_populates="document",
        cascade="all, delete"
    )
    