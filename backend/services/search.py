import html
import re
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def search_google_news(query, limit=6):
    """
    Search Google News RSS for real-time news articles.
    100% free, requires no API key, works on localhost and Render,
    and returns contemporary news within minutes of publication.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            xml_data = resp.read()

        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        articles = []

        for item in items[:limit]:
            raw_title = item.findtext('title') or ''
            raw_link = item.findtext('link') or ''
            raw_desc = item.findtext('description') or ''

            clean_desc = html.unescape(re.sub(r'<[^<]+?>', '', raw_desc)).strip()
            source_elem = item.find('source')
            source_name = source_elem.text if source_elem is not None else ''

            if not raw_title:
                continue

            articles.append({
                "title": raw_title,
                "description": clean_desc or raw_title,
                "content": clean_desc or raw_title,
                "url": raw_link,
                "source": {"name": source_name or "Google News"}
            })

        return articles
    except Exception as e:
        print("Google News Search Error:", str(e))
        return []


def search_wikipedia(query, limit=5):
    """
    Search Wikipedia as an encyclopedic fallback for historical events,
    established facts, or when news search returns 0 articles.
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
        for item in data.get("query", {}).get("search", [])[:4]:
            raw_title = str(item.get("title") or "").strip()
            raw_snippet = str(item.get("snippet") or "").strip()
            clean_snippet = re.sub(r'<[^<]+?>', '', raw_snippet)
            clean_snippet = html.unescape(clean_snippet).strip()
            if not clean_snippet and not raw_title:
                continue

            # Fetch lead summary extract from Wikipedia REST API for richer context
            lead_text = clean_snippet
            try:
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{raw_title.replace(' ', '_')}"
                s_resp = requests.get(summary_url, headers=headers, timeout=5)
                if s_resp.status_code == 200:
                    ext = s_resp.json().get("extract")
                    if ext and len(ext) > len(clean_snippet):
                        lead_text = ext
            except Exception:
                pass

            wiki_articles.append({
                "title": raw_title,
                "description": lead_text,
                "content": lead_text,
                "url": f"https://en.wikipedia.org/wiki/{raw_title.replace(' ', '_')}",
                "source": {"name": "Wikipedia"}
            })
        return wiki_articles
    except Exception as e:
        print("Wikipedia Search Error:", str(e))
        return []


def search_news(query):
    """
    Multi-engine news search:
    1. Google News RSS (breaking news, free, fast)
    2. NewsAPI (if API key available)
    3. Wikipedia fallback (encyclopedic facts)
    """
    # 1. Primary: Google News RSS for real-time news
    articles = search_google_news(query)

    # 2. Secondary: NewsAPI if available and Google News returned 0 articles
    if not articles and NEWS_API_KEY:
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

    # 3. Tertiary Fallback: Wikipedia for historical / established facts
    if not articles:
        articles = search_wikipedia(query)

    return {"articles": articles}

