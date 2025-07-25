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


def get_pdf_filename_from_url(url):
    try:
        parsed = urlparse(url)
        basename = os.path.basename(parsed.path) or "download"
        if not basename.endswith(".pdf"):
            basename += ".pdf"
        return basename
    except Exception as e:
        print(f"[ERROR] Generating PDF filename from URL: {e}")
        return "download.pdf"

def safe_filename_from_url(url):
    try:
        parsed = urlparse(url)
        base = parsed.netloc.replace(".", "_") or "site"
        h = hashlib.sha1(url.encode()).hexdigest()[:8]
        return f"{base}_{h}.txt"
    except Exception as e:
        print(f"[ERROR] Generating safe filename from URL: {e}")
        return "site_unknown.txt"

def save_text_to_file(url, text):
    filename = safe_filename_from_url(url)
    filepath = os.path.join(TEXT_DIR, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"[Source: {url}]\n\n{text}")
        return filepath
    except Exception as e:
        print(f"[ERROR] Writing text file {filepath}: {e}")
        return None

def fetch_page_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        response.encoding = response.apparent_encoding or 'utf-8'

        if "application/pdf" in content_type:
            print(f"[PDF] Downloading: {url}")
            filename = get_pdf_filename_from_url(url)
            path = os.path.join(DOWNLOAD_DIR, filename)

            try:
                with open(path, "wb") as f:
                    f.write(response.content)
                save_to_jsonl({"url": url, "file": path, "type": "pdf"})
                return f"Saved PDF: {path}"
            except Exception as e:
                print(f"[ERROR] Saving PDF: {e}")
                return None

        elif "text/html" in content_type:
            print(f"[HTML] Extracting: {url}")
            try:
                doc = Document(response.text)
                clean_html = doc.summary()
                clean_title = doc.title()
            except Exception as e:
                print(f"[ERROR] Readability parsing failed: {e}")
                return None

            try:
                soup = BeautifulSoup(clean_html, 'html.parser')
                raw_text = soup.get_text(separator=" ", strip=True)
                text = ' '.join(raw_text.split())
                file_path = save_text_to_file(url, text)
                if file_path:
                    save_to_jsonl({
                        "url": url,
                        "file": file_path,
                        "title": clean_title,
                        "type": "html"
                    })
                    return f"Saved main content from: {file_path}"
                else:
                    return None
            except Exception as e:
                print(f"[ERROR] Extracting and saving HTML text: {e}")
                return None

        else:
            print(f"[SKIPPED] Unknown content type: {content_type}")
            return None

    except requests.RequestException as e:
        print(f"[ERROR] Request failed for {url}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None


if __name__ == "__main__":
    urls = [
        "https://en.wikipedia.org/wiki/Nietzsche",
        "https://arxiv.org/pdf/1706.03762.pdf",
        "https://thispagedoesnotexist.org",  # test for failure
    ]

    for url in urls:
        result = fetch_page_content(url)
        print(result)
