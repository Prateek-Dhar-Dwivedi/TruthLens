import html
import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def search_wikipedia(query, limit=5):
    """
    Search Wikipedia as an encyclopedic fallback for historical events,
    established facts, or when NewsAPI returns 0 articles.
    """
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit
        }
        headers = {
            "User-Agent": "TruthLens-FactChecker/1.0 (https://github.com/Prateek-Dhar-Dwivedi/TruthLens)"
        }
        response = requests.get(url, params=params, headers=headers, timeout=8)
        data = response.json()
        wiki_articles = []
        for item in data.get("query", {}).get("search", []):
            raw_title = str(item.get("title") or "").strip()
            raw_snippet = str(item.get("snippet") or "").strip()
            clean_snippet = re.sub(r'<[^<]+?>', '', raw_snippet)
            clean_snippet = html.unescape(clean_snippet).strip()
            if not clean_snippet:
                continue

            wiki_articles.append({
                "title": raw_title,
                "description": clean_snippet,
                "content": clean_snippet,
                "url": f"https://en.wikipedia.org/wiki/{raw_title.replace(' ', '_')}",
                "source": {"name": "Wikipedia"}
            })
        return wiki_articles
    except Exception as e:
        print("Wikipedia Search Error:", str(e))
        return []


def search_news(query):

    articles = []

    if NEWS_API_KEY:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 10,
            "apiKey": NEWS_API_KEY
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=15
            )
            data = response.json()

            if data.get("status") == "ok":
                articles = data.get("articles") or []
            else:
                print("NewsAPI Error:", data.get("message"))

        except Exception as e:
            print("NewsAPI Exception:", str(e))

    # If NewsAPI returned no articles, fallback to Wikipedia search
    if not articles:
        articles = search_wikipedia(query)

    return {"articles": articles}

