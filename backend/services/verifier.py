import os
import google.generativeai as genai
import numpy as np


# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)


def get_embedding(text):

    response = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="semantic_similarity"
    )

    return response["embedding"]



def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    dot = np.dot(a, b)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))



def verify_claim(claim, articles):

    # Generate claim embedding
    claim_embedding = get_embedding(claim)

    scores = []


    for article in articles:

        text = (
            article.get("title", "")
            + " "
            + article.get("description", "")
        )


        # Generate article embedding
        article_embedding = get_embedding(text)


        similarity = cosine_similarity(
            claim_embedding,
            article_embedding
        )


        scores.append(float(similarity))


    return scores
