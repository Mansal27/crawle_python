import requests
from bs4 import BeautifulSoup

def scrape_site(keyword):
    url = f"https://www.google.com/search?q={keyword}&tbm=isch"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    spans = []
    for span in soup.find_all('span'):
        spans.append(span.get_text())
    
    return spans

keyword = "coffee"  # cambia esto con cualquier palabra clave que desees

try:
    result = scrape_site(keyword)
    print(result)
except Exception as e:
    print(e)
