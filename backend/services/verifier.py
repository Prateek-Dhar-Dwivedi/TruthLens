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

        title = article.get(
            "title",
            ""
        )

        description = str(
            article.get(
                "description",
                ""
            ) or ""
        )

        url = (
            article.get("url")
            or
            article.get("link")
            or
            ""
        )

        text = f"{title} {description}"

        similarity = get_similarity(
            claim,
            text
        )

        # Ignore unrelated articles
        if similarity < 0.05:
            continue

        verified_articles.append({

            "title": title,

            "description": description,

            "url": url,

            "text": text,

            "similarity": round(
                similarity * 100,
                2
            )

        })

    verified_articles.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return verified_articles