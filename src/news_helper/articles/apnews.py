from datetime import UTC, datetime, timedelta
from functools import cache
from urllib.parse import urljoin

import dateparser
import httpx
from bs4 import BeautifulSoup
from loguru import logger

# Constants
AP_NEWS_URL = "https://apnews.com/hub/ap-top-news"
TIME_THRESHOLD = datetime.now(tz=UTC) - timedelta(days=1)
ARTICLE_PATH = "/article/"
USER_AGENT = "Mozilla/5.0"


@cache
def get_recent_articles() -> list[str]:
    """Fetch article links from APNews, filtering those containing '/article/' in URL."""
    try:
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=10) as client:
            response = client.get(AP_NEWS_URL)
    except httpx.RequestError as e:
        logger.error(f"An error occurred while fetching APNews: {e}")
        return []

    if response.status_code != 200:
        logger.error(f"Failed to fetch APNews: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    # Find all links containing '/article/'
    for link_tag in soup.find_all("a", href=True):
        href = link_tag["href"]

        if ARTICLE_PATH in href:
            full_url = urljoin("https://apnews.com", href)
            title = link_tag.get_text(strip=True) or "Untitled Article"

            timestamp = link_tag.find("time")
            if timestamp:
                published_time = dateparser.parse(timestamp.get("datetime"))
            else:
                published_time = datetime.now(tz=UTC)  # Default to now if not available

            if published_time and published_time > TIME_THRESHOLD:
                articles.append({"title": title, "url": full_url, "published": published_time})

    if not articles:
        logger.info("No recent articles found.")

    return articles


def extract_article_text(article_url):
    """Extracts article text from an APNews article."""
    try:
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=10) as client:
            response = client.get(article_url)
    except httpx.RequestError as e:
        logger.error(f"An error occurred while fetching the article: {e}")
        return None

    if response.status_code != 200:
        logger.error(f"Failed to fetch article: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Attempt to find article body or default to all <p> tags
    article_body = soup.find("div", {"class": "article-body"})
    if article_body:
        paragraphs = [p.get_text(strip=True) for p in article_body.find_all("p")]
    else:
        logger.warning("Could not find the article body. Extracting all paragraphs.")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

    return "\n".join(paragraphs)
