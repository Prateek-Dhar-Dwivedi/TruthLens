import re
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from huggingface_hub import snapshot_download
from utils.source_score import get_source_score, get_source_label

REFUTATION_PATTERN = re.compile(
    r'\b(false|hoax|fake|untrue|debunk|debunked|debunking|denies|denied|disputed|unfounded|'
    r'fabricated|myth|misleading|incorrect|no evidence|never happened|did not|didn\'t|'
    r'was not|wasn\'t|not true|refutes|refuted|unconfirmed|baseless|no human|never been|'
    r'never landed|refused to buy|did not buy|not made of|isn\'t made of|is not made of)\b',
    re.IGNORECASE
)


# ==========================
# MODEL
# ==========================

try:
    MODEL_DIR = snapshot_download(
        repo_id="Prateek-Dhar-Dwivedi/truthlens-onnx",
        cache_dir="./hf_models"
    )

    MODEL_PATH = f"{MODEL_DIR}/model.onnx"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

    session = ort.InferenceSession(
        MODEL_PATH,
        providers=["CPUExecutionProvider"]
    )

    print("TruthLens ONNX model loaded successfully.")

except Exception as e:
    print("Failed to load ONNX model:", e)
    raise

LABELS = {
    0: "Entailment",
    1: "Neutral",
    2: "Contradiction"
}



# ==========================
# SIMILARITY
# ==========================

def get_similarity(claim, text):

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        vectors = vectorizer.fit_transform(
            [
                claim,
                text
            ]
        )


        return float(
            cosine_similarity(
                vectors[0],
                vectors[1]
            )[0][0]
        )

    except:

        return 0




# ==========================
# NLI
# ==========================

def predict_nli(evidence, claim):


    inputs = tokenizer(

        evidence,

        claim,

        truncation=True,

        padding=True,

        max_length=256,

        return_tensors="np"

    )


    inputs = {

        k:v.astype(np.int64)

        for k,v in inputs.items()

    }


    output = session.run(
        None,
        inputs
    )


    logits = output[0][0]


    exp = np.exp(
        logits - np.max(logits)
    )


    probs = exp / exp.sum()


    index = int(
        np.argmax(probs)
    )


    return {

        "label":
            LABELS[index],

        "score":
            round(
                float(
                    probs[index] * 100
                ),
                2
            )

    }




# ==========================
# FACT CHECK
# ==========================

def check_claim(claim, articles):

    analysis = []

    support_count = 0
    contradict_count = 0
    neutral_count = 0

    total_support_weight = 0.0
    total_contradict_weight = 0.0
    total_neutral_weight = 0.0

    for article in articles:

        if not isinstance(article, dict):
            continue

        title = str(article.get("title") or "").strip()
        description = str(article.get("description") or "").strip()
        content = str(article.get("content") or "").strip()
        url = str(article.get("url") or article.get("link") or "").strip()

        combined_text = f"{title}. {description}".strip()
        if not combined_text:
            continue

        similarity = get_similarity(
            claim,
            combined_text
        )

        # Skip articles with zero topical relevance unless from Wikipedia
        is_wiki = "wikipedia.org" in url.lower()
        if similarity < 0.04 and not is_wiki:
            claim_keywords = [w.lower() for w in claim.split() if len(w) > 4]
            if not any(k in combined_text.lower() for k in claim_keywords):
                continue

        # Candidate premise units: evaluate distinct factual units to find the strongest signal
        candidates = []
        if title:
            candidates.append(title)
        if description:
            candidates.append(description)
        if title and description:
            candidates.append(f"{title}. {description}")

        # Add sentences from description or content
        for block in [description, content]:
            if block:
                s_list = re.split(r'(?<=[.!?])\s+', block)
                for s in s_list:
                    s_clean = s.strip()
                    if 25 < len(s_clean) < 220 and s_clean not in candidates:
                        candidates.append(s_clean)

        best_entailment = None
        best_contradiction = None
        best_neutral = None

        for cand in candidates[:6]:
            nli_res = predict_nli(cand[:256], claim)
            lbl = nli_res["label"]
            sc = nli_res["score"]

            if lbl == "Entailment":
                if best_entailment is None or sc > best_entailment["score"]:
                    best_entailment = {"label": "Entailment", "score": sc, "text": cand}
            elif lbl == "Contradiction":
                if best_contradiction is None or sc > best_contradiction["score"]:
                    best_contradiction = {"label": "Contradiction", "score": sc, "text": cand}
            else:
                if best_neutral is None or sc > best_neutral["score"]:
                    best_neutral = {"label": "Neutral", "score": sc, "text": cand}

        full_context = f"{title} {description} {content}"
        has_explicit_refutation = bool(REFUTATION_PATTERN.search(full_context))

        # Resolution hierarchy:
        # 1. High-confidence Entailment confirms the event
        if best_entailment and best_entailment["score"] >= 65.0:
            final_label = "Entailment"
            final_score = best_entailment["score"]
        # 2. Genuine Contradiction: must have explicit refutation/debunking language
        elif best_contradiction and has_explicit_refutation:
            final_label = "Contradiction"
            final_score = best_contradiction["score"]
        # 3. If model predicted contradiction but text has NO debunking language,
        # it is a missing-premise pseudo-contradiction -> treat as Neutral
        elif best_neutral:
            final_label = "Neutral"
            final_score = best_neutral["score"]
        elif best_contradiction:
            final_label = "Neutral"
            final_score = round(max(50.0, 100.0 - best_contradiction["score"]), 2)
        else:
            final_label = "Neutral"
            final_score = 50.0

        credibility = get_source_score(url)
        cred_factor = max(0.4, credibility / 100.0)
        score_factor = max(0.5, final_score / 100.0)
        sim_factor = max(0.5, min(1.0, max(similarity, article.get("similarity", 0) / 100.0) * 2.2))

        weight = cred_factor * score_factor * sim_factor

        if final_label == "Entailment":
            support_count += 1
            total_support_weight += weight
        elif final_label == "Contradiction":
            contradict_count += 1
            total_contradict_weight += weight
        else:
            neutral_count += 1
            total_neutral_weight += weight * 0.25

        analysis.append({
            "title": title,
            "description": description,
            "url": url,
            "label": final_label,
            "score": final_score,
            "credibility": credibility,
            "credibility_label": get_source_label(credibility)
        })

    # ======================
    # NO EVIDENCE
    # ======================
    if len(analysis) == 0:
        return {
            "claim": claim,
            "verdict": "No Evidence Found",
            "label": "No Evidence Found",
            "score": 0,
            "confidence": 0,
            "support": 0,
            "supports": 0,
            "contradict": 0,
            "contradicts": 0,
            "neutral": 0,
            "analysis": [],
            "evidence": [],
            "explanation": ["No evidence found."]
        }

    # ======================
    # VERDICT DETERMINATION
    # ======================
    decisive_weight = total_support_weight + total_contradict_weight

    if decisive_weight == 0:
        if support_count > 0:
            verdict = "True"
            confidence = 70.0
        elif contradict_count > 0:
            verdict = "False"
            confidence = 70.0
        else:
            verdict = "Uncertain"
            confidence = 0.0

    elif total_support_weight > 0 and total_contradict_weight == 0:
        verdict = "True"
        confidence = round(min(98.5, max(68.0, 75.0 + total_support_weight * 7)), 1)

    elif total_contradict_weight > 0 and total_support_weight == 0:
        verdict = "False"
        confidence = round(min(98.5, max(68.0, 75.0 + total_contradict_weight * 7)), 1)

    elif total_support_weight >= total_contradict_weight * 1.2:
        verdict = "True"
        ratio = total_support_weight / decisive_weight
        confidence = round(min(98.5, max(60.0, ratio * 94.0)), 1)

    elif total_contradict_weight >= total_support_weight * 1.2:
        verdict = "False"
        ratio = total_contradict_weight / decisive_weight
        confidence = round(min(98.5, max(60.0, ratio * 94.0)), 1)

    elif support_count > contradict_count:
        verdict = "True"
        confidence = round(min(80.0, max(52.0, (support_count / max(1, len(analysis))) * 75)), 1)

    elif contradict_count > support_count:
        verdict = "False"
        confidence = round(min(80.0, max(52.0, (contradict_count / max(1, len(analysis))) * 75)), 1)

    else:
        verdict = "Uncertain"
        confidence = 0.0

    return {
        "claim": claim,
        "verdict": verdict,
        "label": verdict,
        "score": confidence,
        "confidence": confidence,
        "supports": support_count,
        "contradicts": contradict_count,
        "support": support_count,
        "contradict": contradict_count,
        "neutral": neutral_count,
        "analysis": analysis,
        "evidence": analysis,
        "explanation": [
            f"AI analyzed {len(analysis)} sources.",
            f"Supporting evidence: {support_count}",
            f"Contradicting evidence: {contradict_count}",
            f"Neutral evidence: {neutral_count}"
        ]
    }
