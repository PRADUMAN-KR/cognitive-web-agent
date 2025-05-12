from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import os
import re

def sanitize_filename(path):
    """
    Convert a URL path to a safe filename by replacing problematic characters.

    Args:
        path (str): The URL path to sanitize.

    Returns:
        str: A sanitized string suitable for use as a filename.
    """
    if not path or path in ['/', '#']:
        return "index"
    path = path.strip().replace('/', '_').replace('\\', '_')
    path = re.sub(r'[^a-zA-Z0-9._-]', '_', path)  
    return path or "index"

def scrape(base_url):
    """
    Scrapes internal links from the base URL, extracts visible text content, and saves it to local text files.

    This function:
    - Fetches the base HTML page
    - Extracts all relative `<a href>` links
    - Downloads each linked page
    - Extracts and saves visible text content to a `scrapped_pages/` folder

    Args:
        base_url (str): The base website URL to scrape from.

    Returns:
        list[dict]: A list of dictionaries containing 'url' and 'text' of each successfully scraped page.
    """
    try:
        response = requests.get(base_url)
        if response.status_code != 200:
            print(f"Failed to load base URL: {base_url}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all('a', href=True)

        hrefs = set()
        for link in links:
            href = link['href']
            if not href.startswith("http"):
                hrefs.add(href)

        scraped_texts = []
        combined_text = ""

        folder_path = "scrapped_pages"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, "combined_scrape.txt")

        for relative_url in hrefs:
            full_url = urljoin(base_url, relative_url)
            try:
                page_response = requests.get(full_url)
                if page_response.status_code == 200:
                    page_soup = BeautifulSoup(page_response.text, "html.parser")
                    page_text = page_soup.get_text(separator="\n", strip=True)
                   
                    combined_text += f"\n\n===== {full_url} =====\n\n{page_text}"
                    scraped_texts.append({'url': full_url, 'text': page_text})
                    print(f"Fetched: {full_url}")

                 

            except Exception as page_error:
                print(f"Error fetching {full_url}: {page_error}")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(combined_text)
        print(f"Saved combined content to: {file_path}")


        return scraped_texts

    except Exception as e:
        print(f"Main scrape error: {e}")
        return []

print(scrape('https://www.ameotech.com/'))
