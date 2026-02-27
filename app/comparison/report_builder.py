def build_report(matched, gaps):

    total = len(matched) + len(gaps)

    coverage = (len(matched) / total * 100) if total else 0
    avg_conf = sum(m["confidence"] for m in matched) / len(matched) if matched else 0

    risk = "Low"
    if coverage < 80:
        risk = "Medium"
    if coverage < 60:
        risk = "High"

    return {
        "matched": matched,
        "gaps": gaps,
        "document_summary": {
            "coverage_percentage": round(coverage, 2),
            "average_confidence": round(avg_conf, 2),
            "gap_count": len(gaps),
            "risk_level": risk
        }
    }