from newspaper import Article
from trafilatura import fetch_url,extract
from bs4 import BeautifulSoup
import requests

def extract_article(url):
    try:
        print("Trying Newspaper3k...")

        article=Article(url)
        article.download()
        article.parse()

        if article.text and len(article.text.strip())>300:
            print("Extracted using Newspaper3k")

            return{
                "title":article.title,
                "text":article.text
            }

        print("Newspaper3k returned empty content")

    except Exception as e:
        print("Newspaper3k failed:",str(e))

    try:
        print("Trying Trafilatura...")

        downloaded=fetch_url(url)

        if downloaded:
            text=extract(downloaded)

            if text and len(text.strip())>300:

                title=url

                try:
                    response=requests.get(
                        url,
                        headers={"User-Agent":"Mozilla/5.0"},
                        timeout=10
                    )

                    soup=BeautifulSoup(
                        response.text,
                        "html.parser"
                    )

                    if soup.title:
                        title=soup.title.text.strip()

                except Exception:
                    pass

                print("Extracted using Trafilatura")

                return{
                    "title":title,
                    "text":text
                }

        print("Trafilatura returned empty content")

    except Exception as e:
        print("Trafilatura failed:",str(e))

    return{
        "error":"Unable to extract article content"
    }