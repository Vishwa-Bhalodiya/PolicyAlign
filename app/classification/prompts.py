from db.seed_domains import DOMAINS

def build_classification_prompt():
    
    domain_list ="\n- " + "\n- ".join(DOMAINS)
    
    return f"""
You are a legal policy classifier.

Classify the following policy sentence into:

1) One Category
2) One Domain from the list below

Categories:
- Obligation
- Prohibition
- Conditional obligation
- Informational
- Scope
- Enforcement
- Regulatory reference
- Heading
- Metadata
- Form field

Domains:
{domain_list}

Return STRICT JSON only:
{{
    "category": "...",
    "domain": "..."
}}

Sentence:
{{sentence}}
"""