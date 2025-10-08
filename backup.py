import os
import re
import requests
import feedparser
from markdownify import markdownify as md
from datetime import datetime
from urllib.parse import urlparse

FEED_URL = "https://alu-ai.blog/feed/"
ARTICLES_DIR = "articles"
IMAGES_DIR = "images"

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")

def download_image(url):
    try:
        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(IMAGES_DIR, filename)
        if not os.path.exists(filepath):
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                print(f"Downloaded image: {filename}")
    except Exception as e:
        print(f"Image download failed ({url}): {e}")

def backup_articles():
    feed = feedparser.parse(FEED_URL)
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        content_html = entry.get("content", [{}])[0].get("value", entry.get("summary", ""))
        content_md = md(content_html)

        img_urls = re.findall(r'(https?://[^\s]+(?:jpg|jpeg|png|gif))', content_html, re.IGNORECASE)
        for img_url in img_urls:
            download_image(img_url)

        filename = sanitize_filename(title) + ".md"
        filepath = os.path.join(ARTICLES_DIR, filename)

        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n")
                f.write(f"[Original Link]({link})\n\n")
                f.write(content_md)
            print(f"Saved article: {filename}")

if __name__ == "__main__":
    print(f"=== Backup started at {datetime.now()} ===")
    backup_articles()
    print("=== Backup completed ===")
