from bs4 import BeautifulSoup
import requests
import os
import re
from browser import BrowserManager, MovieLinkExtractor, MovieScriptScraper, HTMLScriptSaver, PDFScriptSaver

SCRIPT_DIRECTORY = 'movie_scripts'
if not os.path.exists(SCRIPT_DIRECTORY):
    os.makedirs(SCRIPT_DIRECTORY)
# Usage example
if __name__ == '__main__':
    DRIVER_PATH = r'C:\\Omar\\Projects\\Movie Quotes Scraper\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'
    scraper = MovieScriptScraper(DRIVER_PATH)
    
    try:
        scraper.scrape_scripts()
    finally:
        scraper.close()
