import os
import requests

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def get_embedding(text):
    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={"inputs": text},
        timeout=60
    )

    response.raise_for_status()

    return response.json()


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def verify_claim(claim, articles):

    claim_embedding = get_embedding(claim)

    scores = []

    for article in articles:
        text = (
            article.get("title", "") +
            " " +
            article.get("description", "")
        )

        article_embedding = get_embedding(text)

        similarity = cosine_similarity(
            claim_embedding,
            article_embedding
        )

        scores.append(float(similarity))

    return scores
