import requests
import json
import argparse
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_urls_from_html(html, base_url, include_navigation=False):
    soup = BeautifulSoup(html, 'html.parser')
    urls = {a['href'] for a in soup.find_all('a', href=True)}

    if include_navigation:
        for element in soup.find_all(['button', 'div', 'span'], onclick=True):
            onclick_attr = element.get('onclick')
            if 'location.href' in onclick_attr:
                url = onclick_attr.split('location.href=')[1].strip("'\"")
                urls.add(url)

    # Filtrar URLs que comienzan con la URL base
    filtered_urls = [url for url in urls if re.match(rf"^{re.escape(base_url)}", url)]
    return filtered_urls

def crawl(url, user_agent, include_navigation=False):
    response = requests.get(url)
    static_urls = get_urls_from_html(response.text, url, include_navigation)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.get(url)

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
    except Exception as e:
        print(f"Error esperando el contenido dinámico: {e}")

    dynamic_urls = get_urls_from_html(driver.page_source, url, include_navigation)
    driver.quit()

    all_urls = list(set(static_urls + dynamic_urls))
    return all_urls

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawler que extrae URLs de una página web.')
    parser.add_argument('--url', type=str, required=True, help='La URL de la página web a rastrear')
    parser.add_argument('--user_agent', type=str, required=True, help='User-Agent para las solicitudes dinámicas')
    parser.add_argument('--include_navigation', action='store_true', help='Incluir búsqueda en elementos de navegación como botones y divs')

    args = parser.parse_args()
    url = args.url
    user_agent = args.user_agent
    include_navigation = args.include_navigation

    urls = crawl(url, user_agent, include_navigation)
    print(json.dumps(urls, indent=4))
