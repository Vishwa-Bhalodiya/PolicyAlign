from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import SessionLocal
from app.models.domains import ComplianceDomain

MIN_WEIGHT = 1.0
MAX_WEIGHT = 2.5


DOMAINS = [
    {
        "name": "Data Privacy",
        "description": "Protection of personal and sensitive data, consent, and data subject rights",
        "weight": 1.8,
    },
    {
        "name": "Information Security",
        "description": "Confidentiality, integrity, and availability of information assets",
        "weight": 2.0,
    },
    {
        "name": "Access Control & Identity Management",
        "description": "Authentication, authorization, and identity access controls",
        "weight": 1.6,
    },
    {
        "name": "Data Retention & Deletion",
        "description": "Data lifecycle management, retention schedules, and secure deletion",
        "weight": 1.2,
    },
    {
        "name": "Incident Response & Breach Management",
        "description": "Security incident detection, reporting, and response",
        "weight": 1.9,
    },
    {
        "name": "Compliance & Regulatory Obligations",
        "description": "Adherence to laws, regulations, and compliance standards",
        "weight": 2.0,
    },
    {
        "name": "Risk Management",
        "description": "Risk identification, assessment, mitigation, and acceptance",
        "weight": 1.7,
    },
    {
        "name": "Audit & Monitoring",
        "description": "Logging, monitoring, audits, and compliance reviews",
        "weight": 1.5,
    },
    {
        "name": "Business Continuity & Disaster Recovery",
        "description": "Continuity planning, backups, and disaster recovery processes",
        "weight": 1.8,
    },
    {
        "name": "Third-Party & Vendor Management",
        "description": "Vendor risk management and third-party compliance controls",
        "weight": 1.6,
    },
    {
        "name": "Operational Security",
        "description": "Operational procedures ensuring secure system usage",
        "weight": 1.4,
    },
    {
        "name": "Governance & Policy Management",
        "description": "Policy ownership, approvals, governance, and updates",
        "weight": 1.3,
    },
    {
        "name": "Legal & Contractual Terms",
        "description": "Legal obligations, contracts, liabilities, and enforcement",
        "weight": 1.7,
    },
    {
        "name": "Employee Awareness & Training",
        "description": "Security awareness programs and employee responsibilities",
        "weight": 1.1,
    },
    {
        "name": "Ethics & Code of Conduct",
        "description": "Ethical standards, integrity, and professional conduct",
        "weight": 1.0,
    },
]

def seed_domains():
    db: Session = SessionLocal()
    
    created = 0
    updated = 0
    
    try:
        for domain_data in DOMAINS:
            
            name = domain_data["name"].strip()
            weight = float(domain_data["weight"])
            
            if not (MIN_WEIGHT <= weight <= MAX_WEIGHT):
                raise ValueError(
                    f"Weight for {name} must be between {MIN_WEIGHT} and {MAX_WEIGHT}"
                )
                
                
            existing = (
                db.query(ComplianceDomain)
                .filter(ComplianceDomain.name == name.lower())
                .first()
            )
            
            if existing:
                existing.description = domain_data["description"]
                existing.weight = weight
                updated += 1
                
            else:
                new_domain = ComplianceDomain(
                    name=name,
                    description=domain_data["description"],
                    weight=weight
                )
                db.add(new_domain)
                created += 1
            
        db.commit()
        
        print("=====================================")
        print("Domain Seeding Completed Successfully")
        print("Created:", created)
        print("Updated:", updated)
        print("=====================================")
        
    except Exception as e:
        db.rollback()
        print("Error while seeding domains:", e)
        
    finally:
        db.close()
        
if __name__ == "__main__":
    seed_domains()