from app.db.database import SessionLocal
from app.comparison.semantic_matcher import match_client_paragraph
# 🔥 Register all models manually (since main.py is not used)
import app.models.documents
import app.models.paragraph
import app.models.paragraph_classification
import app.models.domains


db = SessionLocal()

client_paragraph_id = 55  # 🔥 PUT REAL CLIENT PARAGRAPH ID HERE

result = match_client_paragraph(db, client_paragraph_id)

if result:
    print("\nCLIENT PARAGRAPH:\n")
    print(result["client_paragraph"])

    print("\nDOMAIN:", result["domain"])

    print("\nMATCHED VENDOR PARAGRAPHS:\n")
    for match in result["matched_vendor_paragraphs"]:
        print("Score:", match["score"])
        print("Text:", match["text"])
        print("------")
else:
    print("No classification found for this paragraph.")

db.close()
