import re
from collections import Counter

def normalize(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lower())

def looks_like_metadata(line: str) -> bool:

    stripped = line.strip()

    # 1️⃣ Very short pure numeric lines (page numbers)
    if re.fullmatch(r"\d+", stripped):
        return True

    # 2️⃣ Page indicators
    if re.search(r"page\s+\d+", stripped, re.IGNORECASE):
        return True

    # 3️⃣ Common footer patterns
    if re.search(
        r"(confidential|all rights reserved|copyright)",
        stripped,
        re.IGNORECASE
    ):
        return True

    # 4️⃣ Lines that are mostly non-letters (e.g., separators)
    alpha_ratio = sum(c.isalpha() for c in stripped) / max(len(stripped), 1)
    if alpha_ratio < 0.25:
        return True

    return False


def detect_repeated_lines(lines, min_repeats=3):

    normalized = [normalize(l) for l in lines if l.strip()]
    counts = Counter(normalized)

    return {
        line for line, c in counts.items()
        if c >= min_repeats and len(line) > 10
    }
