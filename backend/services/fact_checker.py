import os
import requests

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def check_claim(claim, evidence):
    text = f"""
Claim: {claim}

Evidence: {evidence}
"""

    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": [
                "supports claim",
                "contradicts claim",
                "neutral"
            ]
        }
    }

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    return {
        "label": result["labels"][0],
        "score": float(result["scores"][0])
    }
