import re

def normalize_claim(claim: str) -> str:
    """
    Lightweight rule-based claim normalizer that standardizes colloquial
    syntax, handles conversational negation patterns, and expands emerging acronyms
    without adding latency or external API calls.
    """
    if not claim:
        return ""

    normalized = claim.strip()

    # 1. Strip trailing punctuation
    if normalized.endswith("?"):
        normalized = normalized[:-1].strip()

    # 2. Strip conversational question starters
    starters = [
        "is it true that ",
        "is it real that ",
        "did ",
        "does ",
        "do ",
        "is ",
        "are ",
        "was ",
        "were ",
        "has ",
        "have "
    ]
    lower = normalized.lower()
    for starter in starters:
        if lower.startswith(starter):
            normalized = normalized[len(starter):].strip()
            break

    # 3. Normalize colloquial negation/preference syntax:
    # "X no but Y yes" or "X no Y yes" -> "replace X with Y"
    normalized = re.sub(
        r'\b([a-zA-Z0-9]+)\s+no\s+(?:but\s+)?([a-zA-Z0-9]+)\s+yes\b',
        r'replace \1 with \2',
        normalized,
        flags=re.IGNORECASE
    )

    # 4. Contextual acronym expansion for recent events (e.g. SI -> Super Intelligence)
    if re.search(r'\b(ai|trump|technology|tech|musk|intelligence)\b', normalized, re.IGNORECASE):
        normalized = re.sub(r'\bSI\b', 'Super Intelligence', normalized)
        normalized = re.sub(r'\bsi\b', 'Super Intelligence', normalized)

    # 5. Clean excessive whitespace
    return " ".join(normalized.split())