from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from rich import print
from dotenv import load_dotenv
load_dotenv()


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Tool Creation


# This tool uses the Tavily API to search the web for recent and reliable information on a given topic. It returns the titles, URLs, and snippets of the search results.
@tool
def scrape_website(query: str) -> str:
    """Search the web for the recent and reliable information on a topic. Return titles, URLs, and snippets of the search results."""
    results = tavily.search(query=query, max_results=5)
    out = []
    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n")
    return "\n".join(out)


# print(scrape_website.invoke("What is the latest news on Peddi Movie?"))

# This tool scrapes the content of a given URL and returns clean text context for deeper reading. It uses the requests library to fetch the webpage and BeautifulSoup to parse and extract the text while removing unnecessary elements like scripts and styles.
@tool
def scrape_url(url:str) -> str:
    """Scrape and return clean text context from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        return soup.get_text(separator='\n', strip=True)[:3000]
    except Exception as e:
        return f"Error scraping URL: {str(e)}"
