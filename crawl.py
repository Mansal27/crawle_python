import re
import requests
import sys
from urllib.parse import urlparse

def get_domain_base(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

# Obtén el contenido HTML de la URL proporcionada
url_provided = sys.argv[1]
html_content = requests.get(url_provided).text

# Extraer el dominio base de la URL proporcionada
domain_base = get_domain_base(url_provided)

# Define el patrón regex
pattern = r'\b(?:http[s]?://|www\.|[\w\-]+\.[a-z]{2,})(?!.*\.(?:js|css|jpg|jpeg|png|gif|svg|ico))(?:(?:[^\s"\'\(\)])*[^\s"\'\(\)\.])?\b'

# Encuentra todas las coincidencias
matches = re.findall(pattern, html_content)

# Filtra las URLs que contienen el dominio base de la URL proporcionada
similar_urls = [url for url in matches if domain_base in url]

# Especifica la ruta del archivo
ruta_archivo = 'crawleado.txt'

# Abre el archivo en modo escritura ('w') para ponerlo en blanco
with open(ruta_archivo, 'w') as archivo:
    pass

# Abre el archivo en modo adjuntar ('a') y escribe cada URL con un número de línea
with open(ruta_archivo, 'a') as archivo:
    for i, match in enumerate(similar_urls, start=1):
        archivo.write(f"{i}: {match}\n")
