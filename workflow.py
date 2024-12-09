'''
# import requests
# from bs4 import BeautifulSoup

# # URL of the main page with movie scripts
# url = 'https://www.imsdb.com'
# response = requests.get(url)
# soup = BeautifulSoup(response.text, 'lxml')

# # Find all movie links on the page
# movie_links = []
# movies = soup.find_all('a', href=True)

# for movie in movies:
#     if "/Movie Scripts/" in movie['href']:  # Filter for movie script pages
#         movie_links.append(url + movie['href'])

# # Display the first few movie links
# print(movie_links[:5])
# print(f"Total movie links: {len(movie_links)}")
# from selenium import webdriver
# from bs4 import BeautifulSoup
# from selenium.webdriver.chrome.service import Service


# # Set up Selenium WebDriver
# service = Service(r'C:\\Omar\\Projects\\Movie Quotes Scraper\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')

# # Initialize WebDriver with the Service object
# driver = webdriver.Chrome(service=service)
# driver.get("https://www.simplyscripts.com/movie-screenplays.html")

# # Extract the page source once it's loaded
# html = driver.page_source
# soup = BeautifulSoup(html, 'lxml')

# # Find the script (example: <div> containing the script)
# script_text = soup.find('div', class_='script-content').get_text()

# # Save the script text to a file
# with open('simplyscript_movie.txt', 'w') as f:
#     f.write(script_text)

# driver.quit()

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import time
import os

# Set up Selenium WebDriver
service = Service(r'C:\\Omar\\Projects\\Movie Quotes Scraper\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service)

# Create a folder to save all scripts
if not os.path.exists('movie_scripts'):
    os.makedirs('movie_scripts')

# Load the main SimplyScripts page containing the list of movie scripts
driver.get("https://www.simplyscripts.com/movie-screenplays.html")

# Extract the page source once it's loaded
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

# Find all script links (anchors inside <a> tags) on the page
script_links = soup.find_all('a', href=True)

# Filter for links that are likely to contain movie scripts based on their URL or link text
# SimplyScripts contains many non-script links, so we refine the criteria
script_links = [link for link in script_links if 'scripts' in link['href'] or 'screenplay' in link['href']]

# Loop through each script link and scrape the script text
for link in script_links:
    script_url = link['href']
    
    # Ensure the link is complete (if it's a relative link, we make it absolute)
    if not script_url.startswith('http'):
        script_url = 'https://www.simplyscripts.com/' + script_url
    
    # Visit each script's page
    driver.get(script_url)
    time.sleep(3)  # Wait for the page to load (adjust if needed)

    # Extract the new page's HTML
    script_html = driver.page_source
    script_soup = BeautifulSoup(script_html, 'lxml')
    
    # Find the <div> or other container holding the script text (adjust this based on the actual HTML structure)
    script_text_container = script_soup.find('div', class_='script-content')
    
    if script_text_container:
        script_text = script_text_container.get_text()

        # Save each script to a separate text file
        script_title = link.get_text().strip().replace(' ', '_').replace('/', '_')  # Sanitize title for filename
        script_filename = f"movie_scripts/{script_title}.txt"
        
        with open(script_filename, 'w', encoding='utf-8') as f:
            f.write(script_text)
        print(f"Saved: {script_filename}")
    else:
        print(f"Script content not found for: {script_url}")

# Close the browser once done
driver.quit()
'''
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
# chrome_options.add_argument('--incognito')
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--disable-web-security')
# chrome_options.add_argument('--allow-running-insecure-content')
service = Service(r'C:\\Omar\\Projects\\Movie Quotes Scraper\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Create a folder to store scripts
if not os.path.exists('movie_scripts'):
    os.makedirs('movie_scripts')

# List of alphabetical pages (0-9, A-Z)
# alphabet_pages = [str(i) for i in range(1)] + [chr(c) for c in range(ord('O'), ord('Z') + 1)]
alphabet_pages = [chr(c) for c in range(ord('O'), ord('Z') + 1)]

# Loop through each alphabetical page
for letter in alphabet_pages:
    url = f'https://imsdb.com/alphabetical/{letter}'
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    # Extract the page source
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # Find all movie links (assuming they follow the structure provided)
    movie_links = soup.find_all('a', href=True, title=True)
    print(f"Found {len(movie_links)} movie links on page {letter}")
    # print(movie_links[3:6])
    movie_links=movie_links[3:]
    for movie_link in movie_links:
        movie_name = movie_link.text.strip()
        movie_url = 'https://imsdb.com' + movie_link['href']
        movie_name = re.sub(r'[<>:"/\\|?*]', '', movie_name)
        
        # Navigate to each movie's individual page
        driver.get(movie_url)
        time.sleep(2)

        # Extract movie's script page
        movie_html = driver.page_source
        movie_soup = BeautifulSoup(movie_html, 'lxml')
        
        # Find the link to the actual script (html or pdf)
        script_link = movie_soup.find('a', href=True, string=lambda string: string and "Read" in string)
        if script_link:
            script_url = script_link['href']
            
            # Complete the script URL if necessary
            if not script_url.startswith('http'):
                script_url = 'https://imsdb.com' + script_url
            
            # Check if it's an HTML or PDF file
            if script_url.endswith('.html'):
                # Handle HTML script
                driver.get(script_url)
                time.sleep(2)
                script_html = driver.page_source
                script_soup = BeautifulSoup(script_html, 'lxml')

                # Extract the script text (based on the structure of IMSDb HTML scripts)
                script_text = script_soup.get_text()

                # Save as a text file
                script_filename = f"movie_scripts/{movie_name}.txt"
                with open(script_filename, 'w', encoding='utf-8') as f:
                    f.write(script_text)
                print(f"Saved HTML script for {movie_name}")
            
            elif script_url.endswith('.pdf'):
                # Handle PDF script
                response = requests.get(script_url)
                if response.status_code == 200:
                    script_filename = f"movie_scripts/{movie_name}.pdf"
                    with open(script_filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded PDF script for {movie_name}")
                else:
                    print(f"Failed to download PDF for {movie_name}")
        else:
            print(f"Script link not found for {movie_name}")

# Close the browser once done
driver.quit()
