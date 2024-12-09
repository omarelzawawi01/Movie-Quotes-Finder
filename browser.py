import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import re
import os
SCRIPT_DIRECTORY = 'movie_scripts'
class BrowserManager:
    """Manages the Selenium WebDriver setup, navigation, and teardown."""
    
    def __init__(self, driver_path):
        chrome_options = Options()
        self.service = Service(driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
    
    def get_page(self, url):
        """Navigates to a given URL and ensures page load."""
        self.driver.get(url)
        time.sleep(2)  # Adjust sleep for page loading if necessary

    def get_html(self):
        """Retrieves the page source."""
        return self.driver.page_source

    def close(self):
        """Closes the WebDriver session."""
        self.driver.quit()
class MovieLinkExtractor:
    """Extracts movie script links from a specified alphabetical page."""
    
    BASE_URL = 'https://imsdb.com/alphabetical/'

    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
    
    def get_movie_links(self, letter):
        """Fetches movie links for a specific alphabetical letter page."""
        url = f"{self.BASE_URL}{letter}"
        self.browser_manager.get_page(url)
        soup = BeautifulSoup(self.browser_manager.get_html(), 'lxml')
        # Skip irrelevant links at the top of the page
        return soup.find_all('a', href=True, title=True)[3:]  
    
class ScriptSaver:
    """Factory for saving scripts based on their format (.html or .pdf)."""
    
    @staticmethod
    def save_script(movie_name, script_url, browser_manager):
        """Decides between saving as HTML or PDF."""
        if script_url.endswith('.html'):
            return HTMLScriptSaver.save_html_script(movie_name, script_url, browser_manager)
        elif script_url.endswith('.pdf'):
            return PDFScriptSaver.save_pdf_script(movie_name, script_url)

class HTMLScriptSaver:
    """Saves HTML scripts by scraping and saving only relevant content in .txt files."""

    @staticmethod
    def save_html_script(movie_name, script_url, browser_manager):
        browser_manager.get_page(script_url)
        soup = BeautifulSoup(browser_manager.get_html(), 'lxml')
        
        # Extract content inside the <pre> tag
        script_content = soup.find('pre')
        if script_content:
            sanitized_name = re.sub(r'[<>:"/\\|?*]', '', movie_name)
            file_path = f"{SCRIPT_DIRECTORY}/{sanitized_name}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"{sanitized_name}\n\n{script_content.get_text()}")
            print(f"Saved HTML script for {sanitized_name}")
            return file_path
        else:
            print(f"No <pre> content found for {movie_name}")
            return None

class PDFScriptSaver:
    """Downloads and saves PDF scripts."""

    @staticmethod
    def save_pdf_script(movie_name, script_url):
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '', movie_name)
        response = requests.get(script_url)
        if response.status_code == 200:
            file_path = f"{SCRIPT_DIRECTORY}/{sanitized_name}.pdf"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded PDF script for {sanitized_name}")
            return file_path
        else:
            print(f"Failed to download PDF for {sanitized_name}")
            return None

class MovieScriptScraper:
    """Facade class managing the movie script scraping process."""
    
    def __init__(self, driver_path):
        self.browser_manager = BrowserManager(driver_path)
        self.link_extractor = MovieLinkExtractor(self.browser_manager)
    
    def scrape_scripts(self):
        alphabet_pages = [str(i) for i in range(10)] + [chr(c) for c in range(ord('A'), ord('Z') + 1)]
        
        for letter in alphabet_pages:
            movie_links = self.link_extractor.get_movie_links(letter)
            print(f"Found {len(movie_links)} movie links on page {letter}")

            for link in movie_links:
                movie_name = link.text.strip()
                movie_url = 'https://imsdb.com' + link['href']
                
                # Navigate to each movie's page
                self.browser_manager.get_page(movie_url)
                movie_soup = BeautifulSoup(self.browser_manager.get_html(), 'lxml')
                
                # Find the script link
                script_link = movie_soup.find('a', href=True, string=lambda s: s and "Read" in s)
                if script_link:
                    script_url = 'https://imsdb.com' + script_link['href'] if not script_link['href'].startswith('http') else script_link['href']
                    
                    # Save script using the appropriate saver
                    ScriptSaver.save_script(movie_name, script_url, self.browser_manager)
                else:
                    print(f"Script link not found for {movie_name}")

    def close(self):
        """Closes the browser."""
        self.browser_manager.close()
