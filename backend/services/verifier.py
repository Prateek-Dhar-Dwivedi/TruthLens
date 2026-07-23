from sentence_transformers import SentenceTransformer
from sentence_transformers import util

model = SentenceTransformer("all-MiniLM-L6-v2")

def verify_claim(claim, articles):

    claim_embedding = model.encode(
        claim,
        convert_to_tensor=True
    )

    scores = []

    for article in articles:
        text = (article.get("title", "") + " " + article.get("description", ""))

        article_embedding = model.encode(
            text,
            convert_to_tensor=True
        )

        similarity = util.cos_sim(
            claim_embedding,
            article_embedding
        )

        scores.append(float(similarity))

    return scores