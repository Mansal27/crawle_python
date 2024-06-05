import requests
import json
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Función para extraer URLs de un HTML usando BeautifulSoup
def get_urls_from_html(html, include_navigation=False):
    soup = BeautifulSoup(html, 'html.parser')
    urls = {a['href'] for a in soup.find_all('a', href=True)}

    # Solo capturar enlaces en botones u otros elementos de navegación si es necesario
    if include_navigation:
        for element in soup.find_all(['button', 'div', 'span'], onclick=True):
            onclick_attr = element.get('onclick')
            if 'location.href' in onclick_attr:
                url = onclick_attr.split('location.href=')[1].strip("'\"")
                urls.add(url)

    # Filtrar strings vacíos
    return [url for url in urls if url]

# Función para rastrear una página web y extraer URLs
def crawl(url, include_navigation=False, depth=1, current_depth=0, visited=None):
    if visited is None:
        visited = set()

    if current_depth >= depth or url in visited:
        return []

    visited.add(url)
    
    # Paso 1: Usar requests para obtener contenido estático
    response = requests.get(url)
    static_urls = get_urls_from_html(response.text, include_navigation)

    # Paso 2: Usar selenium para obtener contenido dinámico
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.get(url)

    # Espera explícita para asegurar que los elementos dinámicos se carguen
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
    except Exception as e:
        print(f"Error esperando el contenido dinámico: {e}")

    # Obtener el HTML renderizado por el navegador
    dynamic_urls = get_urls_from_html(driver.page_source, include_navigation)
    driver.quit()

    # Combinar y eliminar duplicados
    all_urls = list(set(static_urls + dynamic_urls))

    # Recursivamente rastrear cada URL encontrada hasta la profundidad especificada
    for u in all_urls:
        all_urls.extend(crawl(u, include_navigation, depth, current_depth + 1, visited))

    # Eliminar duplicados y retornar
    return list(set(all_urls))

# Bloque principal para manejar argumentos de línea de comandos y ejecutar el rastreo
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawler que extrae URLs de una página web.')
    parser.add_argument('--url', type=str, required=True, help='La URL de la página web a rastrear')
    parser.add_argument('--include_navigation', action='store_true', help='Incluir búsqueda en elementos de navegación como botones y divs')
    parser.add_argument('--depth', type=int, default=2, help='Profundidad de recursión para el rastreo')
    
    args = parser.parse_args()
    url = args.url
    include_navigation = args.include_navigation
    depth = args.depth

    # Ejecuta la función de rastreo y imprime las URLs en formato JSON
    urls = crawl(url, include_navigation, depth)
    print(json.dumps(urls, indent=4))
