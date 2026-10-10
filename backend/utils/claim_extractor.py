import re

COMMON_TYPOS = {
    r'\bdonalad\b': 'donald',
    r'\bdonld\b': 'donald',
    r'\bdonlad\b': 'donald',
    r'\bpresidnet\b': 'president',
    r'\bgoverment\b': 'government',
    r'\belone\b': 'elon',
    r'\bmusck\b': 'musk',
}

def normalize_claim(claim: str) -> str:
    """
    Lightweight rule-based claim normalizer that corrects common entity typos,
    standardizes colloquial syntax, handles question starters, and expands
    emerging acronyms without adding latency or external API calls.
    """
    if not claim:
        return ""

    normalized = claim.strip()

    # 1. Strip trailing punctuation
    if normalized.endswith("?"):
        normalized = normalized[:-1].strip()

    # 2. Correct common typos in names and entities
    for pat, rep in COMMON_TYPOS.items():
        normalized = re.sub(pat, rep, normalized, flags=re.IGNORECASE)

    # 3. Strip conversational question starters
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

    # 4. Normalize colloquial negation/preference syntax:
    # "X no but Y yes" or "X no Y yes" -> "replace X with Y"
    normalized = re.sub(
        r'\b([a-zA-Z0-9]+)\s+no\s+(?:but\s+)?([a-zA-Z0-9]+)\s+yes\b',
        r'replace \1 with \2',
        normalized,
        flags=re.IGNORECASE
    )

    # 5. Contextual acronym expansion for recent events (e.g. SI -> Super Intelligence)
    if re.search(r'\b(ai|trump|technology|tech|musk|intelligence)\b', normalized, re.IGNORECASE):
        normalized = re.sub(r'\bSI\b', 'Super Intelligence', normalized)
        normalized = re.sub(r'\bsi\b', 'Super Intelligence', normalized)

    # 6. Clean excessive whitespace
    return " ".join(normalized.split())

def extract_search_keywords(claim: str) -> str:
    """
    Extract high-value search tokens by removing low-signal conversational stop words.
    """
    stop_words = {
        "says", "said", "say", "to", "the", "a", "an", "is", "are",
        "was", "were", "by", "for", "in", "on", "at", "with", "from",
        "that", "this", "it", "and", "or", "but", "about", "into"
    }
    words = [w for w in claim.split() if w.lower() not in stop_words]
    return " ".join(words)