from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# TEXT SIMILARITY
# =========================

def get_similarity(text1, text2):

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        vectors = vectorizer.fit_transform(
            [
                text1,
                text2
            ]
        )

        similarity = cosine_similarity(
            vectors[0],
            vectors[1]
        )[0][0]

        return float(similarity)

    except Exception:

        return 0.0


# =========================
# VERIFY CLAIM
# =========================

def verify_claim(claim, articles):

    verified_articles = []

    for article in articles:

        if not isinstance(article, dict):
            continue

        title = str(article.get("title") or "").strip()
        description = str(article.get("description") or "").strip()
        content = str(article.get("content") or "").strip()
        url = str(article.get("url") or article.get("link") or "").strip()

        # Build comprehensive representation for similarity matching
        parts = [p for p in [title, description, content] if p]
        text = ". ".join(parts) if parts else ""

        similarity = get_similarity(
            claim,
            text
        )

        verified_articles.append({
            "title": title,
            "description": description,
            "content": content,
            "url": url,
            "text": text,
            "similarity": round(
                similarity * 100,
                2
            ),
            "sim_raw": similarity
        })

    verified_articles.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    # Tier 1: Strong semantic relevance (>= 15% cosine similarity)
    high_relevance = [a for a in verified_articles if a["sim_raw"] >= 0.15]
    if high_relevance:
        return high_relevance

    # Tier 2: Moderate relevance fallback (>= 8% similarity)
    medium_relevance = [a for a in verified_articles if a["sim_raw"] >= 0.08]
    if medium_relevance:
        return medium_relevance

    # Tier 3: If similarities are low across all articles, take top 3 candidates
    return verified_articles[:3] if verified_articles else []