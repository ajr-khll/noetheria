import requests
from bs4 import BeautifulSoup
import json
import time

def save_to_jsonl(text, link, filename="information.jsonl"):
    with open(filename, 'a', encoding='utf-8') as f:
        json.dump({"url": link, "text": text}, f, ensure_ascii=False)
        f.write('\n')

def fetch_page_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator="\n", strip=True)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    

if __name__ == "__main__":
    pass