import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from huggingface_hub import snapshot_download


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


    support = 0

    contradict = 0

    neutral = 0




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
            )
            or ""
        )



        url = (

            article.get("url")

            or

            article.get("link")

            or

            ""

        )



        text = (

            title

            +

            " "

            +

            description

        )



        similarity = get_similarity(
            claim,
            text
        )


        if similarity < 0.05:

            continue



        result = predict_nli(
            text,
            claim
        )


        label = result["label"]

        score = result["score"]




        if label == "Entailment":

            support += 1


        elif label == "Contradiction":

            contradict += 1


        else:

            neutral += 1




        analysis.append({

            "title":
                title,

            "description":
                description,

            "url":
                url,

            "label":
                label,

            "score":
                score,

            "credibility":
                50,

            "credibility_label":
                "Medium"

        })





    # ======================
    # NO EVIDENCE
    # ======================

    if len(analysis) == 0:


        return {


            "claim":
                claim,


            "verdict":
                "No Evidence Found",


            "label":
                "No Evidence Found",


            "score":
                0,


            "confidence":
                0,


            "support":
                0,


            "supports":
                0,


            "contradict":
                0,


            "contradicts":
                0,


            "neutral":
                0,


            "analysis":
                [],


            "evidence":
                []

        }





    # ======================
    # VERDICT
    # ======================

    if support > contradict:

        verdict = "True"


    elif contradict > support:

        verdict = "False"


    else:

        verdict = "Uncertain"




    total = (
        support
        +
        contradict
        +
        neutral
    )



    confidence = round(

        (
            max(
                support,
                contradict
            )

            /

            total

        )

        *

        100,

        2

    )





    return {


        "claim":
            claim,


        # frontend

        "verdict":
            verdict,


        # app.py

        "label":
            verdict,



        # both app.py and frontend

        "score":
            confidence,


        "confidence":
            confidence,



        # frontend

        "supports":
            support,


        "contradicts":
            contradict,



        # app.py

        "support":
            support,


        "contradict":
            contradict,



        "neutral":
            neutral,



        # frontend

        "analysis":
            analysis,



        # app.py

        "evidence":
            analysis,



        "explanation":[

            f"AI analyzed {len(analysis)} sources.",

            f"Supporting evidence: {support}",

            f"Contradicting evidence: {contradict}",

            f"Neutral evidence: {neutral}"

        ]

    }
