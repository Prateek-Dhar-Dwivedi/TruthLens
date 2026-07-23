import os
import google.generativeai as genai


# Get Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)


# Gemini model
model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def check_claim(claim, evidence):

    prompt = f"""
You are a professional fact-checking AI.

Analyze the claim using the provided evidence.

Claim:
{claim}

Evidence:
{evidence}

Classify the claim into exactly one category:
- supports claim
- contradicts claim
- neutral

Also provide a confidence score between 0 and 1.

Return ONLY valid JSON in this format:

{{
    "label": "supports claim | contradicts claim | neutral",
    "score": 0.0,
    "reason": "short explanation"
}}
"""

    response = model.generate_content(prompt)

    result_text = response.text.strip()

    # Remove markdown JSON formatting if Gemini adds it
    result_text = result_text.replace("```json", "")
    result_text = result_text.replace("```", "")

    import json

    result = json.loads(result_text)

    return {
        "label": result["label"],
        "score": float(result["score"]),
        "reason": result["reason"]
    }
