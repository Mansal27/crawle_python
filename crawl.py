import re
import requests
import sys
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

def get_domain_base(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def get_urls_from_html(html_content, pattern, domain_base):
    matches = re.findall(pattern, html_content)
    similar_urls = {url for url in matches if domain_base in url}
    return similar_urls

def crawl(url, pattern, depth, current_depth, domain_base, visited, archivo, headers):
    if current_depth > depth or url in visited:
        return set()
    
    visited.add(url)

    try:
        response = requests.get(url, headers=headers)
        html_content = response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return set()
    
    urls = get_urls_from_html(html_content, pattern, domain_base)

    all_urls = set(urls)
    
    for u in urls:
        if u not in visited:
            all_urls.update(crawl(u, pattern, depth, current_depth + 1, domain_base, visited, archivo, headers))
    
    # Guardar URLs obtenidas en el archivo
    for u in all_urls:
        if u not in visited:
            archivo.write(f"{u}\n")
    
    # Introducir un retraso para evitar activar mecanismos de seguridad
    time.sleep(3)
    
    return all_urls

# Bloque principal para manejar argumentos de línea de comandos y ejecutar el rastreo
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python crawler.py <URL> <depth>")
        sys.exit(1)
    
    url_provided = sys.argv[1]
    depth = int(sys.argv[2])

    # Define el patrón regex
    pattern = r'\b(?:http[s]?://|www\.|[\w\-]+\.[a-z]{2,})(?!.*\.(?:js|css|jpg|jpeg|png|gif|svg|ico))(?:(?:[^\s"\'\(\)])*[^\s"\'\(\)\.])?\b'

    # Extraer el dominio base de la URL proporcionada
    domain_base = get_domain_base(url_provided)

    # Conjunto para almacenar URLs visitadas
    visited = set()

    # Especifica la ruta del archivo
    ruta_archivo = 'crawleado.txt'

    # User-Agent header
    googlebot_user_agent = (
    "ControllerSEO/1.0 (compatible; controllerSEO/1.0; +https://controllerseo.com/)"
)
    headers = {"User-Agent": googlebot_user_agent}
    response = requests.head(href, headers=headers, verify=True, timeout=10)

    # Abre el archivo en modo escritura ('w') para ponerlo en blanco
    with open(ruta_archivo, 'w') as archivo:
        pass

    # Abre el archivo en modo adjuntar ('a') y ejecutar el rastreo
    with open(ruta_archivo, 'a') as archivo:
        all_urls = crawl(url_provided, pattern, depth, 0, domain_base, visited, archivo, headers)

    print("Rastreo completado. URLs guardadas en 'crawleado.txt'.")
