import requests
from bs4 import BeautifulSoup

def scrape_content(url):
    response = requests.get(url)                             #Makes HTTP request to given URL
    soup = BeautifulSoup(response.text, 'html.parser')            
    if response.status_code != 200:
        return None
    text = ' '.join(p.text for p in soup.find_all('p'))      #Parses all <p> tags and join them into a string
    return text
