import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

try:
    from newspaper import Article
except ImportError:
    Article = None

try:
    from trafilatura import fetch_url, extract
except ImportError:
    fetch_url, extract = None, None


def extract_headline_from_url(url):
    """
    Extract readable headline from news URL slug when direct scraping
    is blocked by Cloudflare / DataDome paywalls (e.g. Forbes, Bloomberg, NYT).
    """
    try:
        path = urlparse(url).path.strip('/')
        segments = [s for s in path.split('/') if s]
        if not segments:
            return ""
        slug = segments[-1]
        slug = re.sub(r'\.(html|htm|php|asp|aspx)$', '', slug, flags=re.I)
        if slug.isdigit() and len(segments) > 1:
            slug = segments[-2]
        words = re.split(r'[-_+]+', slug)
        clean_words = [w for w in words if w and not (len(w) > 14 and not any(v in w.lower() for v in 'aeiou'))]
        if len(clean_words) >= 3:
            return " ".join(clean_words).capitalize()
    except Exception:
        pass
    return ""


def extract_article(url):
    """
    Extract article title and text from URL with multi-tiered fallbacks:
    1. Newspaper3k
    2. Trafilatura
    3. BeautifulSoup OpenGraph metadata
    4. URL slug decomposition + Google News RSS resolution (for 403 paywalled sites like Forbes)
    """
    # Tier 1: Newspaper3k
    if Article:
        try:
            print("Trying Newspaper3k...")
            article = Article(url)
            article.download()
            article.parse()

            if article.text and len(article.text.strip()) > 200:
                print("Extracted using Newspaper3k")
                return {
                    "title": article.title,
                    "text": article.text
                }
        except Exception as e:
            print("Newspaper3k failed:", str(e))

    # Tier 2: Trafilatura
    if fetch_url and extract:
        try:
            print("Trying Trafilatura...")
            downloaded = fetch_url(url)
            if downloaded:
                text = extract(downloaded)
                if text and len(text.strip()) > 200:
                    title = url
                    try:
                        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
                        soup = BeautifulSoup(resp.text, "html.parser")
                        if soup.title:
                            title = soup.title.text.strip()
                    except Exception:
                        pass
                    print("Extracted using Trafilatura")
                    return {
                        "title": title,
                        "text": text
                    }
        except Exception as e:
            print("Trafilatura failed:", str(e))

    # Tier 3: BeautifulSoup with full browser headers for OpenGraph tags
    try:
        print("Trying BeautifulSoup OpenGraph tags...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            og_title = soup.find("meta", property="og:title")
            og_desc = soup.find("meta", property="og:description")
            meta_desc = soup.find("meta", attrs={"name": "description"})

            title = og_title["content"].strip() if og_title and og_title.get("content") else ""
            if not title and soup.title:
                title = soup.title.text.strip()

            desc = og_desc["content"].strip() if og_desc and og_desc.get("content") else ""
            if not desc and meta_desc and meta_desc.get("content"):
                desc = meta_desc["content"].strip()

            paras = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 30]
            body_text = "\n\n".join(paras[:10])

            combined_text = f"{desc}\n\n{body_text}".strip()
            if title and len(combined_text) > 100:
                print("Extracted using BeautifulSoup OpenGraph")
                return {
                    "title": title,
                    "text": combined_text
                }
    except Exception as e:
        print("BeautifulSoup fallback failed:", str(e))

    # Tier 4: URL Slug Extraction + Google News RSS Corroboration (for 403 Forbidden / Paywalled sites like Forbes)
    print("Trying URL Slug + Google News Fallback...")
    headline = extract_headline_from_url(url)
    if headline:
        domain = urlparse(url).netloc.lower().replace("www.", "")
        resolved_title = headline
        resolved_text = f"{headline}. Published by {domain}."

        try:
            q = urllib.parse.quote(headline)
            rss_url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
            req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                xml_data = r.read()
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            if items:
                t = items[0].findtext('title') or headline
                d = html.unescape(re.sub(r'<[^<]+?>', '', items[0].findtext('description') or '')).strip()
                resolved_title = t
                resolved_text = f"{d}\n\nOriginal article headline from {domain}: {headline}"
        except Exception as e:
            print("Google News slug resolution error:", e)

        print(f"Extracted paywalled article via URL slug: '{resolved_title}'")
        return {
            "title": resolved_title,
            "text": resolved_text,
            "is_paywalled": True
        }

    return {
        "error": "Unable to extract article content. The publication may require login or block web scrapers."
    }