# parser.py
from bs4 import BeautifulSoup
from transformers import pipeline

ner = pipeline("ner", grouped_entities=True, framework="pt")

def extract_entities(text):
    results = ner(text[:1000])  # limit for speed
    return list(set([r['word'] for r in results if 'ORG' in r['entity_group']]))

def parse_page(url, html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "No Title"
    text = soup.get_text(separator=" ", strip=True)
    entities = extract_entities(text)
    return {
        "url": url,
        "title": title,
        "text": text,
        "entities": entities
    }
