from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

from services.search import search_news
from services.fact_checker import check_claim
from services.explainer import generate_explanation

from database import (
    history_collection,
    users_collection,
    saved_collection,
)

from auth import (
    hash_password,
    verify_password,
    create_token,
    verify_token,
)

from services.article_extractor import extract_article
from bson import ObjectId

from urllib.parse import urlparse

from source_scores import get_source_score
from urllib.parse import urlparse

from database import saved_collection

from utils.source_score import (
    get_source_score,
    get_source_label
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

    claim = data["claim"].strip()

    if len(claim.split()) < 3:
        return {
            "error": "Please enter a complete factual claim."
        }

    news = search_news(claim)

    articles = news.get("articles", [])

    if not articles:
        return {
            "claim": claim,
            "verdict": "No Evidence Found",
            "confidence": 0,
            "supports": 0,
            "contradicts": 0,
            "neutral": 0,
            "analysis": [],
            "explanation": [
                "No relevant news articles were found."
            ]
        }

    claim_words = [
        word.lower()
        for word in claim.split()
        if len(word) > 3
    ]

    results = []

    supports = 0
    contradicts = 0
    neutral = 0

    for article in articles:

        text = (
            article.get("title", "") +
            " " +
            str(article.get("description", ""))
        ).lower()

        matches = sum(
            1 for word in claim_words
            if word in text
        )

        if matches < 2:
            continue

        evidence = (
            article.get("title", "") +
            " " +
            str(article.get("description", ""))
        )

        result = check_claim(
            claim,
            evidence
        )

        label = result["label"]
        score = round(
            result["score"],
            3
        )

        if score < 0.50:
            continue

        if label == "supports claim":
            supports += 1

        elif label == "contradicts claim":
            contradicts += 1

        else:
            neutral += 1
            
        credibility = get_source_score(
         article.get("url", "")
           )
        
        results.append({
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "label": label,
            "score": score,
            "credibility": credibility,
            "credibility_label": get_source_label(
        credibility
    )
            })

    if not results:
        return {
            "claim": claim,
            "verdict": "No Evidence Found",
            "confidence": 0,
            "supports": 0,
            "contradicts": 0,
            "neutral": 0,
            "analysis": [],
            "explanation": [
                "No sufficiently relevant evidence was found."
            ]
        }

    if supports > contradicts:
        verdict = "Likely True"

    elif contradicts > supports:
        verdict = "Likely False"

    else:
        verdict = "Uncertain"

    total = supports + contradicts + neutral

    confidence = round(
        max(supports, contradicts) / total * 100,
        2
    )

    explanation = generate_explanation(results)

    current_user = get_current_user(
    data.get("token")
    )

    history_collection.insert_one({
        "email": current_user,
        "claim": claim,
        "verdict": verdict,
        "confidence": confidence,
        "supports": supports,
        "contradicts": contradicts,
        "neutral": neutral,
        "createdAt": datetime.utcnow()
    })

    return {
        "claim": claim,
        "verdict": verdict,
        "confidence": confidence,
        "supports": supports,
        "contradicts": contradicts,
        "neutral": neutral,
        "analysis": results,
        "explanation": explanation
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
def fact_check_url(data:dict):
    
    url=data["url"]

    original_domain=urlparse(
        url
    ).netloc.lower()

    article=extract_article(url)

    if "error" in article:
        return{
            "error":article["error"]
        }

    title=article["title"]

    text=article["text"]

    junk_phrases=[
        "is a senior reporter",
        "joined The Verge",
        "daily email digest",
        "homepage feed",
        "Posts from this author",
        "Subscribe",
        "Sign up",
        "Advertisement"
    ]

    for phrase in junk_phrases:

        if phrase in text:

            pos=text.find(phrase)

            next_period=text.find(
                ".",
                pos
            )

            if next_period!=-1:

                text=text[
                    next_period+1:
                ]

    text=" ".join(
        text.split()
    )

    claim=title

    news=search_news(
        claim
    )

    articles=news.get(
        "articles",
        []
    )

    if not articles:

        search_query=" ".join(
            title
            .replace(":"," ")
            .replace(","," ")
            .replace("'","")
            .split()[:8]
        )

        news=search_news(
            search_query
        )

        articles=news.get(
            "articles",
            []
        )

    if not articles:

        search_query=" ".join(
            text.split()[:25]
        )

        news=search_news(
            search_query
        )

        articles=news.get(
            "articles",
            []
        )

    if not articles:

        return{
            "article_title":title,
            "verdict":"No Evidence Found",
            "confidence":0,
            "supports":0,
            "contradicts":0,
            "neutral":0,
            "analysis":[],
            "article_preview":text[:1000]
        }

    same_domain_articles=[]
    other_articles=[]

    for item in articles:

        evidence_url=item.get(
            "url",
            ""
        )

        evidence_domain=urlparse(
            evidence_url
        ).netloc.lower()

        if evidence_domain==original_domain:

            same_domain_articles.append(
                item
            )

        else:

            other_articles.append(
                item
            )

    if other_articles:
        articles=other_articles

    else:
        articles=same_domain_articles

    results=[]

    supports=0
    contradicts=0
    neutral=0

    for item in articles:

        evidence_url=item.get(
            "url",
            ""
        )

        evidence=(
            item.get(
                "title",
                ""
            )
            +
            " "
            +
            str(
                item.get(
                    "description",
                    ""
                )
            )
        )

        result=check_claim(
            claim,
            evidence
        )

        score=round(
            result["score"],
            3
        )

        if score<0.5:
            continue

        label=result["label"]

        if label=="supports claim":

            supports+=1

        elif label=="contradicts claim":

            contradicts+=1

        else:

            neutral+=1
        
        credibility = get_source_score(
    evidence_url
          )
        
        results.append({
            "title":item.get(
                "title",
                ""
            ),
            "url":evidence_url,
            "label":label,
            "score":score,
            "credibility": credibility,
            "credibility_label": get_source_label(
        credibility
            )
        })

    results.sort(
        key=lambda x:x["score"],
        reverse=True
    )

    if not results:

        return{
            "article_title":title,
            "verdict":"Insufficient Evidence",
            "confidence":0,
            "supports":0,
            "contradicts":0,
            "neutral":0,
            "analysis":[],
            "article_preview":text[:1000]
        }

    verdict="Uncertain"

    if supports>contradicts:

        verdict="Likely True"

    elif contradicts>supports:

        verdict="Likely False"

    total=(
        supports+
        contradicts+
        neutral
    )

    confidence=(
        round(
            max(
                supports,
                contradicts
            )/total*100,
            2
        )
        if total>0
        else 0
    )

    return{
        "article_title":title,
        "verdict":verdict,
        "confidence":confidence,
        "supports":supports,
        "contradicts":contradicts,
        "neutral":neutral,
        "analysis":results,
        "article_preview":text[:1000]
    }
@app.post("/ask")
def ask_ai(data: dict):

    question = data.get("question", "").strip()

    if not question:
        return {
            "error": "Question is required"
        }

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

    return fact_check({
        "claim": claim,
        "token": data.get("token")
    })
    
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