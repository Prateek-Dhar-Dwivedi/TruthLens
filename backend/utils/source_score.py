from urllib.parse import urlparse

SOURCE_SCORES = {

    "reuters.com":95,
    "apnews.com":95,
    "bbc.com":92,
    "bbc.co.uk":92,
    "nytimes.com":90,
    "wsj.com":90,
    "bloomberg.com":90,
    "economist.com":90,

    "thehindu.com":85,
    "indianexpress.com":85,
    "hindustantimes.com":82,
    "timesofindia.indiatimes.com":80,
    "ndtv.com":80,

    "news18.com":75,
    "zeenews.india.com":70,

}

def get_source_score(url):

    domain = urlparse(
        url
    ).netloc.lower()

    domain = domain.replace(
        "www.",
        ""
    )

    for source,score in SOURCE_SCORES.items():

        if source in domain:

            return score

    return 50

def get_source_label(score):

    if score >= 90:
        return "Trusted"

    if score >= 75:
        return "Reliable"

    if score >= 60:
        return "Moderate"

    return "Low Credibility"