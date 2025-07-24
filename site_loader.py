import requests
from bs4 import BeautifulSoup
import os
import json
import hashlib
from urllib.parse import urlparse
from readability import Document

DOWNLOAD_DIR = "downloaded_pdfs"
TEXT_DIR = "site_texts"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

def save_to_jsonl(record, filename="information.jsonl"):
    with open(filename, 'a', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False)
        f.write('\n')

def get_pdf_filename_from_url(url):
    parsed = urlparse(url)
    basename = os.path.basename(parsed.path)
    if not basename.endswith(".pdf"):
        basename += ".pdf"
    return basename

def safe_filename_from_url(url):
    parsed = urlparse(url)
    base = parsed.netloc.replace(".", "_")  # e.g. en_wikipedia_org
    h = hashlib.sha1(url.encode()).hexdigest()[:8]
    return f"{base}_{h}.txt"

def save_text_to_file(url, text):
    filename = safe_filename_from_url(url)
    filepath = os.path.join(TEXT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"[Source: {url}]\n\n{text}")
    return filepath

def fetch_page_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "application/pdf" in content_type:
            print(f"[PDF] Downloading: {url}")
            filename = get_pdf_filename_from_url(url)
            path = os.path.join(DOWNLOAD_DIR, filename)

            with open(path, "wb") as f:
                f.write(response.content)

            save_to_jsonl({"url": url, "file": path, "type": "pdf"})
            return f"Saved PDF: {path}"

        elif "text/html" in content_type:
            print(f"[HTML] Extracting: {url}")
            response.encoding = response.apparent_encoding
            doc = Document(response.text)
            clean_html = doc.summary()
            clean_title = doc.title()

            soup = BeautifulSoup(clean_html, 'html.parser')
            raw_text = soup.get_text(separator=" ", strip=True)
            text = ' '.join(raw_text.split())

            file_path = save_text_to_file(url, text)
            save_to_jsonl({"url": url, "file": file_path, "title": clean_title, "type": "html"})
            return f"Saved main content from: {file_path}"

        else:
            print(f"[SKIPPED] Unknown content type: {content_type}")
            return None

    except requests.RequestException as e:
        print(f"[ERROR] {url}: {e}")
        return None

if __name__ == "__main__":
    # Example:
    urls = [
        "https://en.wikipedia.org/wiki/Nietzsche",
        "https://arxiv.org/pdf/1706.03762.pdf"
    ]

    for url in urls:
        fetch_page_content(url)
