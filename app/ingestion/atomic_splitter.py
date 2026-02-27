import re
from typing import List

OBLIGATION_TRIGGERS = [
    "shall",
    "must",
    "required to",
    "is required to",
    "are required to",
    "prohibited",
    "shall not",
    "must not"
]

def split_into_atomic(text: str) -> List[str]:
    """
    Splits paragraph into atomic compliance sentences.
    """

    # First split by punctuation
    rough_sentences = re.split(r"[.;]", text)

    atomic_sentences = []

    for sentence in rough_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Split chained obligations
        lower = sentence.lower()

        splits = re.split(
            r"\b(?:shall|must|required to|prohibited|shall not|must not)\b",
            sentence,
            flags=re.IGNORECASE
        )

        if len(splits) > 1:
            # Reattach trigger words
            matches = re.findall(
                r"\b(?:shall|must|required to|prohibited|shall not|must not)\b",
                sentence,
                flags=re.IGNORECASE
            )

            for i in range(len(matches)):
                atomic_sentences.append(
                    (matches[i] + " " + splits[i+1]).strip().capitalize()
                )
        else:
            atomic_sentences.append(sentence)

    return atomic_sentences