from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import os
import time
import re

# Set up Selenium WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
service = Service(r'C:\\Omar\\Projects\\Movie Quotes Scraper\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Create a folder to store scripts
if not os.path.exists('movie_scripts'):
    os.makedirs('movie_scripts')

# List of alphabetical pages (0-9, A-Z)
# alphabet_pages = [chr(c) for c in range(ord('O'), ord('Z') + 1)]
alphabet_pages = [str(i) for i in range(1)] + [chr(c) for c in range(ord('A'), ord('Z') + 1)]

# Loop through each alphabetical page
for letter in alphabet_pages:
    url = f'https://imsdb.com/alphabetical/{letter}'
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    # Extract the page source
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # Find all movie links
    movie_links = soup.find_all('a', href=True, title=True)
    movie_links = movie_links[3:]  # Skip irrelevant links at the top of the list
    print(f"Found {len(movie_links)} movie links on page {letter}")

    for movie_link in movie_links:
        movie_name = movie_link.text.strip()
        movie_url = 'https://imsdb.com' + movie_link['href']
        sanitized_movie_name = re.sub(r'[<>:"/\\|?*]', '', movie_name)  # Sanitize movie name

        # Navigate to each movie's individual page
        driver.get(movie_url)
        time.sleep(2)

        # Extract movie's script page
        movie_html = driver.page_source
        movie_soup = BeautifulSoup(movie_html, 'lxml')

        # Find the link to the actual script
        script_link = movie_soup.find('a', href=True, string=lambda s: s and "Read" in s)
        if script_link:
            script_url = 'https://imsdb.com' + script_link['href'] if not script_link['href'].startswith('http') else script_link['href']

            if script_url.endswith('.html'):
                # Handle HTML script
                driver.get(script_url)
                time.sleep(2)
                script_html = driver.page_source
                script_soup = BeautifulSoup(script_html, 'lxml')

                # Extract the title and script content inside <pre> tag
                title = sanitized_movie_name
                script_content = script_soup.find('pre')
                if script_content:
                    # Format content for saving
                    script_text = f"{title}\n\n{script_content.get_text()}"
                    
                    # Save as a text file
                    script_filename = f"movie_scripts/{sanitized_movie_name}.txt"
                    with open(script_filename, 'w', encoding='utf-8') as f:
                        f.write(script_text)
                    print(f"Saved HTML script for {title}")
                else:
                    print(f"Script content not found in expected format for {title}")

            elif script_url.endswith('.pdf'):
                # Handle PDF script
                response = requests.get(script_url)
                if response.status_code == 200:
                    script_filename = f"movie_scripts/{sanitized_movie_name}.pdf"
                    with open(script_filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded PDF script for {sanitized_movie_name}")
                else:
                    print(f"Failed to download PDF for {sanitized_movie_name}")
        else:
            print(f"Script link not found for {movie_name}")

# Close the browser once done
driver.quit()
