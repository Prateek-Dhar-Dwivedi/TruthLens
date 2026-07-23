from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

def check_claim(claim, evidence):

    text = f"""
    Claim: {claim}

    Evidence: {evidence}
    """

    result = classifier(
        text,
        candidate_labels=[
            "supports claim",
            "contradicts claim",
            "neutral"
        ]
    )

    return {
        "label": result["labels"][0],
        "score": float(result["scores"][0])
    }