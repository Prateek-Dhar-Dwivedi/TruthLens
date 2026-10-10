from datetime import datetime
from urllib.parse import urlparse

from bson import ObjectId
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

from auth import (
    hash_password,
    verify_password,
    create_token,
    verify_token
)

from database import (
    history_collection,
    users_collection,
    saved_collection
)

from services.article_extractor import extract_article
from services.explainer import generate_explanation
from services.fact_checker import check_claim
from services.search import search_news, search_wikipedia
from services.verifier import verify_claim

from utils.source_score import (
    get_source_score,
    get_source_label
)
from utils.claim_extractor import (
    normalize_claim,
    extract_search_keywords
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_current_user(authorization: str = Header(None)):

    if not authorization:
        return None

    payload = verify_token(authorization)

    if not payload:
        return None

    return payload["email"]
    
@app.get("/")
def home():
    return {
        "message": "TruthLens API Running"
    }

@app.post("/register")
def register(data: dict):

    email = data["email"]
    password = data["password"]

    existing = users_collection.find_one({
        "email": email
    })

    if existing:
        return {
            "error": "User already exists"
        }

    users_collection.insert_one({
        "email": email,
        "password": hash_password(password)
    })

    return {
        "message": "User created successfully"
    }

@app.post("/login")
def login(data: dict):

    email = data["email"]
    password = data["password"]

    user = users_collection.find_one({
        "email": email
    })

    if not user:
        return {
            "error": "User not found"
        }

    if not verify_password(
        password,
        user["password"]
    ):
        return {
            "error": "Invalid password"
        }

    token = create_token(email)

    return {
        "token": token
    }

@app.post("/fact-check")
def fact_check(data: dict):

    try:
        original_claim = str(data.get("claim", "")).strip()

        if len(original_claim.split()) < 3:
            return {
                "error": "Please enter a complete factual claim."
            }

        # Normalize claim to handle colloquial phrasing, questions, typos, and modern acronyms
        normalized_claim = normalize_claim(original_claim)

        # 1. Search news using normalized claim first
        news = search_news(normalized_claim)
        articles = news.get("articles") or []

        # 2. If no articles found, search core keywords (removes filler words and punctuation)
        if not articles:
            keywords = extract_search_keywords(normalized_claim)
            if keywords and keywords != normalized_claim:
                news = search_news(keywords)
                articles = news.get("articles") or []

        # 3. If still no articles, fallback to original query
        if not articles and normalized_claim != original_claim:
            news = search_news(original_claim)
            articles = news.get("articles") or []

        # Filter out unrelated articles using similarity with normalized claim
        verified_articles = verify_claim(
            normalized_claim,
            articles
        )

        target_articles = verified_articles if verified_articles else articles[:5]

        # 4. If target_articles is empty or has very low similarity (< 0.08), query Wikipedia fallback
        max_sim = max((a.get("sim_raw", 0) for a in target_articles), default=0.0)
        if not target_articles or max_sim < 0.08:
            wiki_articles = search_wikipedia(normalized_claim)
            if wiki_articles:
                verified_wiki = verify_claim(normalized_claim, wiki_articles)
                if verified_wiki:
                    target_articles = (target_articles or []) + verified_wiki

        if not target_articles:
            return {
                "claim": original_claim,
                "verdict": "No Evidence Found",
                "confidence": 0,
                "supports": 0,
                "contradicts": 0,
                "neutral": 0,
                "analysis": [],
                "explanation": [
                    "No evidence found."
                ]
            }

        # Run ONNX model on relevant articles
        result = check_claim(
            normalized_claim,
            target_articles
        )

        # If news analysis yielded Uncertain (e.g. only peripheral/neutral articles found), query Wikipedia
        if result["verdict"] == "Uncertain" or (result["supports"] == 0 and result["contradicts"] == 0):
            wiki_articles = search_wikipedia(normalized_claim)
            if wiki_articles:
                verified_wiki = verify_claim(normalized_claim, wiki_articles)
                if verified_wiki:
                    wiki_result = check_claim(normalized_claim, verified_wiki)
                    if wiki_result["verdict"] in ["True", "False"]:
                        result = wiki_result

        try:
            current_user = get_current_user(data.get("token"))
            if current_user:
                history_collection.insert_one({
                    "email": current_user,
                    "claim": original_claim,
                    "verdict": result["verdict"],
                    "confidence": result["confidence"],
                    "supports": result["supports"],
                    "contradicts": result["contradicts"],
                    "neutral": result["neutral"],
                    "createdAt": datetime.utcnow()
                })
        except Exception as db_err:
            print("Database save error (non-fatal):", db_err)

        return {
            "claim": original_claim,
            "verdict": result["verdict"],
            "confidence": result["confidence"],
            "supports": result["supports"],
            "contradicts": result["contradicts"],
            "neutral": result["neutral"],
            "analysis": result["analysis"],
            "explanation": result["explanation"]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "claim": original_claim if 'original_claim' in locals() else "",
            "verdict": "Uncertain",
            "confidence": 0,
            "supports": 0,
            "contradicts": 0,
            "neutral": 0,
            "analysis": [],
            "explanation": [f"Verification completed with uncertainty: {str(e)}"],
            "error_detail": str(e)
        }
    
@app.get("/my-history")
def my_history(
    authorization: str = Header(None)
):

    email = get_current_user(
        authorization
    )

    if not email:
        return {
            "error": "Unauthorized"
        }

    records = []

    for item in history_collection.find({
        "email": email
    }).sort(
        "createdAt",
        -1
    ):

        records.append({
            "id": str(item["_id"]),
            "claim": item["claim"],
            "verdict": item["verdict"],
            "confidence": item["confidence"]
        })

    return records

@app.get("/history")
def get_history():

    records = []

    for item in history_collection.find().sort(
        "createdAt",
        -1
    ):

        records.append({
            "id": str(item["_id"]),
            "claim": item["claim"],
            "verdict": item["verdict"],
            "confidence": item["confidence"]
        })

    return records

@app.delete("/history/{id}")
def delete_history(id: str):

    history_collection.delete_one({
        "_id": ObjectId(id)
    })

    return {
        "message": "History deleted"
    }

@app.delete("/history")
def clear_history():

    history_collection.delete_many({})

    return {
        "message": "All history cleared"
    }

@app.get("/stats")
def get_stats():

    total_checks = history_collection.count_documents({})

    true_claims = history_collection.count_documents({
        "verdict": "Likely True"
    })

    false_claims = history_collection.count_documents({
        "verdict": "Likely False"
    })

    uncertain_claims = history_collection.count_documents({
        "verdict": "Uncertain"
    })

    return {
        "total_checks": total_checks,
        "true_claims": true_claims,
        "false_claims": false_claims,
        "uncertain_claims": uncertain_claims
    }
    
@app.post("/fact-check-url")
def fact_check_url(data: dict):

    url = data.get("url", "").strip()

    if not url:
        return {"error": "Please enter a valid URL"}

    # -------------------------
    # Extract article
    # -------------------------

    article = extract_article(url)

    if "error" in article:
        return {
            "error": article["error"]
        }

    title = article["title"]
    text = article.get("text", "")

    # Clean title for news search (strip source publisher suffix like ' - Forbes')
    import re
    search_title = re.sub(r'\s*-\s*[A-Za-z0-9\s]+$', '', title).strip()

    # -------------------------
    # Search related news
    # -------------------------

    news = search_news(search_title)
    articles = news.get("articles", [])

    if not articles and search_title != title:
        news = search_news(title)
        articles = news.get("articles", [])

    if not articles:
        search_query = " ".join(
            title.replace(":", " ")
                 .replace(",", " ")
                 .replace("'", "")
                 .split()[:8]
        )
        news = search_news(search_query)
        articles = news.get("articles", [])

    if not articles:
        return {
            "article_title": title,
            "verdict": "No Evidence Found",
            "confidence": 0,
            "supports": 0,
            "contradicts": 0,
            "neutral": 0,
            "analysis": [],
            "article_preview": text[:1000]
        }

    # -------------------------
    # Remove same-domain sources if other sources exist
    # -------------------------

    original_domain = urlparse(url).netloc.lower().replace("www.", "")

    filtered_articles = []

    for item in articles:
        evidence_url = item.get("url", "")
        evidence_domain = urlparse(evidence_url).netloc.lower().replace("www.", "")
        if evidence_domain != original_domain:
            filtered_articles.append(item)

    target_articles = filtered_articles if filtered_articles else articles

    # -------------------------
    # Verify Similarity
    # -------------------------

    verified_articles = verify_claim(
        search_title,
        target_articles
    )

    if not verified_articles:
        verified_articles = target_articles[:5]

    # -------------------------
    # ONNX Fact Check
    # -------------------------

    result = check_claim(
        search_title,
        verified_articles
    )

    # -------------------------
    # Return
    # -------------------------

    return {
        "article_title": title,
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "supports": result["supports"],
        "contradicts": result["contradicts"],
        "neutral": result["neutral"],
        "analysis": result["analysis"],
        "article_preview": text[:1000],
        "explanation": result["explanation"],
        "disclaimer": result.get("disclaimer", "TruthLens AI can make mistakes. Please verify critical facts with official sources.")
    }
    
@app.post("/ask")
def ask_ai(data: dict):

    question = data.get("question", "").strip()

    if not question:
        return {"error": "Question is required"}

    claim = question

    if claim.endswith("?"):
        claim = claim[:-1]

    starters = [
        "did ",
        "does ",
        "do ",
        "is ",
        "are ",
        "was ",
        "were ",
        "has ",
        "have "
    ]

    lower = claim.lower()

    for starter in starters:
        if lower.startswith(starter):
            claim = claim[len(starter):]
            break

    response = fact_check({
        "claim": claim,
        "token": data.get("token")
    })

    return response
    
@app.get("/trending-news")
def trending_news():

    news = search_news("latest news")

    articles = news.get("articles", [])[:10]

    return [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "source": item.get("source", {}).get("name")
        }
        for item in articles
    ]
    
@app.post("/save-check")
def save_check(data: dict):

    email = get_current_user(
        data.get("token")
    )

    if not email:
        return {
            "error":"Unauthorized"
        }

    saved_collection.insert_one({
        "email": email,
        "claim": data.get("claim"),
        "verdict": data.get("verdict"),
        "confidence": data.get("confidence"),
        "createdAt": datetime.utcnow()
    })

    return {
        "message":"Saved successfully"
    }

@app.get("/saved-checks")
def get_saved_checks(
    authorization:str=Header(None)
):

    email = get_current_user(
        authorization
    )

    if not email:
        return []

    results=[]

    for item in saved_collection.find(
        {"email":email}
    ).sort(
        "createdAt",
        -1
    ):

        results.append({
            "id":str(item["_id"]),
            "claim":item["claim"],
            "verdict":item["verdict"],
            "confidence":item["confidence"]
        })

    return results

@app.delete("/saved-check/{id}")
def delete_saved_check(id:str):

    saved_collection.delete_one({
        "_id":ObjectId(id)
    })

    return {
        "message":"Deleted"
    }
