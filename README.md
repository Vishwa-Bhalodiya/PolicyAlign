# Policy Compliance & Document Alignment System

An AI-powered compliance intelligence system that compares client policy documents against vendor policies to determine regulatory alignment, identify obligation gaps, and generate structured compliance reports.

This system combines:
- Semantic embeddings (SentenceTransformers)
- LLM-based legal reasoning (Mistral via Langchain)
- Domain-based paragraph classification
- Atomic obligation analysis
- Gap detection & remediation suggestions

---

## Project Overview

Organizations often need to assess whether vendor policies satisfy internal internal regulatory and compliance requirements.

Manual review is:
- Time-consuming
- Subjective
- Inconsistent
- Difficult to scale

This system automates:
1. Policy Ingestion
2. Paragraph classification by domain
3. Atomic obligation extraction
4. Semantic comparison
5. Substantial satisfaction determination
6. Gap analysis
7. Remediation suggestion generation
8. Structured compliance reporting

---

## Core Architecture

### 1. Document Ingestion:
- Policy Documents are split into paragraphs
- Paragraphs are stored in the database
- Domain classification is applied

**Modules:**
```bash
app/ingestion/
  paragraph_splitter.py
  atomic_splitter.py
```

### 2. Domain Classification:
Each paragraph is classified into a regulatory domain such as:
- Compliance & Regulatory Obligations
- Information Security
- Governance
- Risk Management
- Enforcement

**Modules:**
```bash
app/classification/
  domain_classifier.py
  atomic_classifier.py
  prompts.py
```

### 3. Vector Search (Embedding Layer):
- Vendor paragraphs are embedded using:
```bash
all-mpnet-base-v2
```
- Domain-aware vector search retrieves top candidates
  
**Module:**
```bash
app/comparison/vector_store.py
```

### 4. AI-Based Semantic Matching:
The system evaluates whether a vendor paragraph substantially satisfies a client obligation.

**Evaluation Criteria:**
- Equivalent scope
- Equivalent regulatory refrence
- Equivalent inplementation obligation
- Equivalent enforcement requirement

**LLM Used:**
- mistral-small-latest
- Deterministic (temperature=0)
- Strict JSON response format

**Module:**
```bash
app/comparison/semantic_matcher.py
```

### 5. Atomic-Level Matching:
Client paragraphs are decomposed into atomic obligations to ensure precise gap detection.

**Module:**
```bash
app/comparison/atomic_matcher.py
```

### 6. Gap Analysis:
If no vendor paragraph substantially satisfies the obligation:
- Marked as unmatched
- Classified as compliance gap

**Module:**
```bash
app/comparison/gap_analyzer.py
```

### 7. Remediation Engine:
Automatically generates suggested vendor language to close identified gaps.

**Module:**
```bash
app/comparison/remediation.py
```

### 8. Report Builder:
Produces structured JSON output:
- Matched obligations
- Unmatched obligations
- Confidence scores
- Gap explanations
- Suggested remediation text

**Module:**
```bash
app/comparison/report_builder.py
```

## System Folw

```bash
Client Document
        ↓
Paragraph Split
        ↓
Atomic Obligation Extraction
        ↓
Domain Classification
        ↓
Vendor Vector Search
        ↓
AI Substantial Satisfaction Analysis
        ↓
Match / Gap Determination
        ↓
Structured Compliance Report
```


## Output Example
```bash
{
    "matched": [
        {
            "client_paragraph": "Information must be protected against unauthorized access, disclosure, alteration, and destruction.",
            "client_domain": "Information Security",
            "vendor_paragraph_id": 201,
            "vendor_paragraph": "This framework establishes mandatory standards to ensure confidentiality, integrity, and availability of organizational information.",
            "vendor_domain": "Information Security",
            "embedding_score": 0.54,
            "ai_score": 0.91,
            "final_score": 0.76,
            "confidence": 0.76,
            "reason": "Confidentiality, integrity, and availability collectively address protection against unauthorized access, disclosure, alteration, and destruction."
        }
    ],
    "unmatched_client_paragraphs": [
        {
            "client_atomic": "This policy shall be reviewed annually to ensure continued regulatory compliance.",
            "gap_type": "Completely absent obligation",
            "reason": "No explicit annual review requirement or regulatory compliance trigger found.",
            "suggested_vendor_text": "VENDOR:\nThis framework shall be reviewed at least once per year and updated as necessary to ensure ongoing regulatory compliance.",
            "closet_vendor_text": "This framework shall undergo periodic evaluation to ensure continued relevance and effectiveness.",
            "closet_embedding_score": 0.58,
            "ai_similarity_score": null
        }
    ],
    "document_summary": {
        "total_client_paragraphs": 2,
        "matched_count": 1,
        "coverage_percentage": 50.0,
        "average_confidence": 0.76
    }
}
```

---

## Tech Stack
- Python 3.11.9
- FastAPI
- SQLAlchemy
- SentenceTransformers
- LangChain
- Mistral AI
- PostgreSQL
- Custome domain-aware vector store

---

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/Vishwa-Bhalodiya/PolicyAlign/tree/main
cd policy-compliance-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create **.env** file:
```bash
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
MISTRAL_API_KEY=your_api_key
```

### 5. Run Application
```bash
uvicorn app.main:app --reload
```

---

## Key Features
- Domain-aware semantic matching
- AI-based substantial satisfaction evaluation
- Atomic obligation detection
- Gap identification
- Remediation suggestion generation
- Structured compliance reporting
- Confidence scoring
- Deterministic LLM output

---

## Matching Logic Philosophy
The system does NOT rely solely on embedding similarity.

Final match determination requires:

- AI confirmation of substantial satisfaction
- Weighted scoring between embedding and AI similarity
- Domain-aware penalty adjustments

This prevents false positive and reduces inflated compliance coverage.

---

## Compliance Philosophy
This system is designed to be:
- Conservative
- Defensible
- Audit-friendly
- Legally structured

It prioritized explicit obligation equivalence over vague governance language.

---

## Future Enhancement
- Partial Satisfaction category
- Risk scoring engine
- Multi-document batch comparison
- UI dashboard
- Compliance heatmap visualization
- Continuous improvement detection engine
- Role-based access control
- Enterprise logging & monitoring

---


 
