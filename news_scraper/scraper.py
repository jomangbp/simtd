#######################################
# IMPORTS
#######################################
import logging
import time
from typing import List, Dict, Optional

# Import the Crawl4AI crawler from the unclecode/crawl4ai repository.
# Ensure that the Crawl4AI package is installed in your environment.
from crawl4ai import Crawler

#######################################
# CLASSES
#######################################
class NewsScraper:
    """
    NewsScraper uses the Crawl4AI library to scrape market news from a specified website.
    It fetches the latest news headlines and filters them by keywords if provided.
    """

    def __init__(self, base_url: str = "https://crawl4ai.com/mkdocs/", crawl_delay: int = 5):
        """
        Initializes the NewsScraper with a base URL and a crawl delay.
        
        :param base_url: The URL to scrape news from.
        :param crawl_delay: Delay (in seconds) between crawls.
        """
        self.base_url = base_url
        self.crawl_delay = crawl_delay
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            logging.basicConfig(level=logging.DEBUG)

    def get_latest_news(self, keywords: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Uses the Crawl4AI library to crawl the base URL for news items.
        Optionally filters the news items based on the provided keywords.
        
        :param keywords: List of keywords to filter news headlines.
        :return: A list of dictionaries containing 'headline', 'link', and 'timestamp'.
        """
        try:
            # Initialize the crawler from Crawl4AI with the base URL.
            crawler = Crawler(url=self.base_url)
            self.logger.info(f"Starting crawl on {self.base_url}")
            # Run the crawler; assume crawl() returns a list of news items.
            news_results = crawler.crawl()
            # Respect the crawl delay between requests.
            time.sleep(self.crawl_delay)
        except Exception as e:
            self.logger.error(f"Error during crawling: {e}")
            return []

        # Process the crawled news items.
        filtered_news = []
        for item in news_results:
            # Assume each news item is a dictionary with keys 'title', 'url', and 'date'.
            headline = item.get("title", "").strip()
            link = item.get("url", self.base_url).strip()
            timestamp = item.get("date", str(time.time()))

            # If keywords are provided, filter out headlines that do not contain any keyword.
            if keywords and not any(keyword.lower() in headline.lower() for keyword in keywords):
                continue

            filtered_news.append({
                "headline": headline,
                "link": link,
                "timestamp": timestamp
            })

        self.logger.info(f"Retrieved {len(filtered_news)} news items after filtering.")
        return filtered_news

#######################################
# FUNCTIONS OUTSIDE OF CLASSES
#######################################
def print_latest_news(keywords: Optional[List[str]] = None) -> None:
    """
    Helper function to instantiate the NewsScraper, fetch the latest news,
    and print the headlines to the console.
    
    :param keywords: Optional list of keywords to filter news items.
    """
    scraper = NewsScraper()
    news_items = scraper.get_latest_news(keywords=keywords)
    if not news_items:
        print("No news items found.")
        return
    print("Latest News Headlines:")
    for news in news_items:
        print(f"- {news['headline']} (Link: {news['link']}, Timestamp: {news['timestamp']})")

#######################################
# MAIN EXECUTION BLOCK
#######################################
if __name__ == "__main__":
    # Example usage: Print the latest news containing the keywords "stock" or "market".
    print_latest_news(keywords=["stock", "market"])