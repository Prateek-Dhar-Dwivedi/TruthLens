from urllib.parse import urlparse

SOURCE_SCORES = {

    "reuters.com": 95,
    "apnews.com": 95,
    "nature.com": 96,
    "science.org": 96,
    "bbc.com": 92,
    "bbc.co.uk": 92,
    "nytimes.com": 91,
    "wsj.com": 90,
    "bloomberg.com": 90,
    "economist.com": 90,
    "theguardian.com": 89,
    "washingtonpost.com": 89,
    "cnn.com": 86,
    "time.com": 86,
    "theverge.com": 85,
    "thehindu.com": 85,
    "indianexpress.com": 85,
    "wired.com": 84,
    "techcrunch.com": 84,
    "cnet.com": 84,
    "forbes.com": 83,
    "hindustantimes.com": 82,
    "businessinsider.com": 82,
    "timesofindia.indiatimes.com": 80,
    "macrumors.com": 80,
    "ndtv.com": 80,
    "gizmodo.com": 78,
    "news18.com": 75,
    "ibtimes.com": 70,
    "ibtimes.co.uk": 70,
    "ibtimes.com.au": 70,
    "zeenews.india.com": 70,

}

def get_source_score(url):

    if not url:
        return 50

    try:
        domain = urlparse(url).netloc.lower()
        domain = domain.replace("www.", "")

        for source, score in SOURCE_SCORES.items():
            if source in domain:
                return score
    except Exception:
        pass

    return 50

def get_source_label(score):

    if score >= 90:
        return "Trusted"

    if score >= 75:
        return "Reliable"

    if score >= 60:
        return "Moderate"

    return "Low Credibility"