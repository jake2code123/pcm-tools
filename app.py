from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

# Regex pattern for detecting sold listings
SOLD_PATTERN = re.compile(r"sorry[,!\s]*that ad is no longer available", re.I)

def extract_links(html):
    """Extract all unique https:// links from pasted HTML/code."""
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href.startswith("https://"):
            links.add(href)
    return links

def check_links(links):
    """Fetch each link and determine if it is valid or sold."""
    valid_links = set()
    invalid_links = set()

    for link in links:
        try:
            response = requests.get(link, timeout=10)
            page_text = " ".join(response.text.lower().split())
            if SOLD_PATTERN.search(page_text):
                invalid_links.add(link)
            else:
                valid_links.add(link)
        except Exception:
            # Retry once on transient error
            try:
                response = requests.get(link, timeout=10)
                page_text = " ".join(response.text.lower().split())
                if SOLD_PATTERN.search(page_text):
                    invalid_links.add(link)
                else:
                    valid_links.add(link)
            except:
                invalid_links.add(link)

    return sorted(valid_links), sorted(invalid_links)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/link-extractor', methods=['GET', 'POST'])
def link_extractor():
    valid_links = []
    invalid_links = []

    if request.method == 'POST':
        input_text = request.form.get('input_text', '')
        links = extract_links(input_text)
        valid_links, invalid_links = check_links(links)

    return render_template('link-extractor.html',
                           valid_links=valid_links,
                           invalid_links=invalid_links)

if __name__ == '__main__':
    app.run(debug=True)