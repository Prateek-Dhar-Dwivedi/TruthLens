import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def search_news(query):

    if not NEWS_API_KEY:
        print("ERROR: NEWS_API_KEY not found")
        return {"articles": []}

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

        print("Status Code:", response.status_code)

        data = response.json()

        print("NewsAPI Response:", data)

        if data.get("status") != "ok":
            print("NewsAPI Error:", data.get("message"))
            return {"articles": []}

        return data

    except Exception as e:

        print("NewsAPI Exception:", str(e))

        return {"articles": []}
