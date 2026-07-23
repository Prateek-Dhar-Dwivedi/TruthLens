def get_source_score(url):

    scores = {

        "reuters.com":95,
        "apnews.com":94,
        "bbc.com":92,
        "nytimes.com":91,
        "wsj.com":90,
        "theguardian.com":89,
        "cnn.com":86,
        "theverge.com":85,
        "cnet.com":84,
        "techcrunch.com":84,
        "businessinsider.com":82,
        "macrumors.com":80,
        "gizmodo.com":78

    }

    for domain,score in scores.items():
        if domain in url.lower():
            return score

    return 60