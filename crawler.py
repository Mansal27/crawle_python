import os
import requests
import json
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlparse
from queue import PriorityQueue
import threading
import time
import random
import re

from user_agents import get_random_user_agent
from robots import can_fetch
from csv_handler import initialize_csv, save_url_to_csv, save_content_to_csv

def get_HTML(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error al obtener contenido estático de {url}: {e}")
        return None

def scrape_page(html, base_url, include_navigation):
    soup = BeautifulSoup(html, 'html.parser')
    urls = {urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)}

    if include_navigation:
        for element in soup.find_all(['button', 'div', 'span'], onclick=True):
            onclick_attr = element.get('onclick')
            if 'location.href' in onclick_attr:
                url = onclick_attr.split('location.href=')[1].strip("'\"")
                urls.add(urljoin(base_url, url))

    return [url for url in urls if url]

def is_pagination_url(url):
    pagination_keywords = ['page', 'p=', 'start=', 'pg=']
    return any(keyword in url for keyword in pagination_keywords)

def is_same_domain(url, domain_regex):
    return re.match(domain_regex, urlparse(url).netloc)

def save_html_file(url, html):
    directory = 'html_files'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, f"{re.sub(r'[^a-zA-Z0-9]', '_', url)}.html")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)

def worker(queue, visited, all_urls, include_navigation, max_depth, domain_regex, lock):
    while not queue.empty():
        current_priority, url = queue.get()

        with lock:
            if url in visited or not can_fetch(url):
                continue
            visited.add(url)
            save_url_to_csv(url)

        headers = {'User-Agent': get_random_user_agent()}

        html = get_HTML(url, headers)
        static_urls = []
        if html:
            save_html_file(url, html)
            static_urls = scrape_page(html, url, include_navigation)
            with lock:
                all_urls.extend(static_urls)
                save_content_to_csv(url, ' '.join(static_urls))

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument(f"user-agent={get_random_user_agent()}")
        dynamic_urls = []
        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(5)
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
            dynamic_html = driver.page_source
            dynamic_urls = scrape_page(dynamic_html, url, include_navigation)
            with lock:
                all_urls.extend(dynamic_urls)
                save_content_to_csv(url, ' '.join(dynamic_urls))
            save_html_file(url, dynamic_html)
            driver.quit()
        except Exception as e:
            print(f"Error al obtener contenido dinámico de {url}: {e}")
            if driver:
                driver.quit()
            continue

        combined_urls = set(static_urls + dynamic_urls)
        with lock:
            for next_url in combined_urls:
                if next_url not in visited and is_same_domain(next_url, domain_regex):
                    priority = 1 if is_pagination_url(next_url) else current_priority + 1
                    if current_priority < max_depth:
                        queue.put((priority, next_url))

        time.sleep(random.uniform(1, 3))  # Pausa aleatoria para evitar sobrecarga del servidor

def crawl_page(start_url, include_navigation=False, max_depth=2, num_threads=4):
    if num_threads > 10:  # Limitar el número de hilos a 10 por defecto para evitar problemas de sobrecarga
        num_threads = 10

    parsed_start_url = urlparse(start_url)
    domain_regex = re.compile(rf"^(.*\.)?{re.escape(parsed_start_url.netloc)}$")
    visited = set()
    queue = PriorityQueue()
    queue.put((0, start_url))

    all_urls = []
    threads = []
    lock = threading.Lock()

    initialize_csv()

    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(queue, visited, all_urls, include_navigation, max_depth, domain_regex, lock))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return list(set(all_urls))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawler que extrae URLs de una página web.')
    parser.add_argument('--url', type=str, required=True, help='La URL de la página web a rastrear')
    parser.add_argument('--include_navigation', action='store_true', help='Incluir búsqueda en elementos de navegación como botones y divs')
    parser.add_argument('--depth', type=int, default=2, help='Profundidad de recursión para el rastreo')
    parser.add_argument('--threads', type=int, default=4, help='Número de hilos para el rastreo concurrente')
    
    args = parser.parse_args()
    url = args.url
    include_navigation = args.include_navigation
    depth = args.depth
    num_threads = args.threads

    urls = crawl_page(url, include_navigation, depth, num_threads)
    print(json.dumps(urls, indent=4))
