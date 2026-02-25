from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

# Sold message pattern (robust to spacing & punctuation)
SOLD_PATTERN = re.compile(
    r"sorry[,!\s]*that ad is no longer available",
    re.IGNORECASE
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def extract_links(html):
    """Extract unique https:// links from pasted HTML"""
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("https://"):
            links.add(href)

    return sorted(links)


def check_links(links):
    """Check which links are valid vs sold"""
    valid_links = []
    invalid_links = []

    for link in links:
        try:
            response = requests.get(
                link,
                headers=HEADERS,
                timeout=15
            )

            # Normalize page text (important!)
            page_text = " ".join(response.text.lower().split())

            if SOLD_PATTERN.search(page_text):
                invalid_links.append(link)
            else:
                valid_links.append(link)

        except Exception:
            # Network errors → invalid
            invalid_links.append(link)

    return valid_links, invalid_links


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/link-extractor", methods=["GET", "POST"])
def link_extractor():
    valid_links = []
    invalid_links = []

    if request.method == "POST":
        input_text = request.form.get("input_text", "")
        links = extract_links(input_text)
        valid_links, invalid_links = check_links(links)

    return render_template(
        "link-extractor.html",
        valid_links=valid_links,
        invalid_links=invalid_links
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)