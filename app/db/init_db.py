from app.db.database import engine, Base
from app.models.domains import ComplianceDomain  # IMPORTANT
from app.models.paragraph import Paragraph
from app.models.documents import Document
from app.models.paragraph_classification import ParagraphClassification

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
