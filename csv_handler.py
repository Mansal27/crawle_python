import csv
from datetime import datetime

def initialize_csv():
    with open('urls.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['url', 'timestamp'])

    with open('content.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['url', 'content'])

def save_url_to_csv(url):
    with open('urls.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([url, datetime.now()])

def save_content_to_csv(url, content):
    with open('content.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([url, content])
