import requests

import pyttsx3
from bs4 import BeautifulSoup
import pandas as pd

# Initialize empty lists at the global scope
urls = []
titles = []
descriptions = []

def NewsFromBBC(genre):
    global urls, titles, descriptions  # Declare variables as global

    query_params = {
        "source": f"bbc-{str(genre)}",
        "sortBy": "top",
        "apiKey": "4dbc17e007ab436fb66416009dfb59a8"  # Placeholder API key
    }
    main_url = "https://newsapi.org/v1/articles"

    # Fetching data in json format
    res = requests.get(main_url, params=query_params)
    open_bbc_page = res.json()

    # Clear previous data
    urls.clear()
    titles.clear()
    descriptions.clear()

    # Getting all articles
    articles = open_bbc_page["articles"]

    for article in articles:
        titles.append(article["title"])
        descriptions.append(article.get("description", "No description available."))
        urls.append(article["url"])

    main_content_texts = []
    for url in urls:
      response = requests.get(url)
      if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Attempt to find the main content container. Adjust the selector based on the website's structure.
        # This uses CSS selectors to find elements that are likely to contain the main content.
        # Common examples include <main>, <article>, or <div> elements with specific class attributes.
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='main-content')

        # If a main content container is found, extract all paragraph texts from it
        if main_content:
            article_text = ' '.join(p.text for p in main_content.find_all('p'))
            main_content_texts.append(article_text)

    df=pd.DataFrame()
    df['Title']=titles
    df['desc']=descriptions
    df['content']=main_content_texts
    df.to_csv('sports.csv')

# Driver Code
if __name__ == '__main__':
    NewsFromBBC("sport")

