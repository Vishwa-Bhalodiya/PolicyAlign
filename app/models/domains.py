from sqlalchemy import Column, Integer, String, Boolean, Float
from app.db.database import Base

class ComplianceDomain(Base):
    __tablename__ = "compliance_domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
