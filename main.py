import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import google_search
import site_loader
import prompt_optimizer
import json

load_dotenv()

prompt = input("Enter Prompt: ")


google_queries = prompt_optimizer.prompt_optimization(prompt)
print(f"\nOptimized Google Search Queries:\n{google_queries.strip()}")


queries = [q.strip() for q in google_queries.strip().split('\n') if q.strip()]



def fetch_links(query):
    print(f"Fetching links for query: {query}")
    return google_search.fetch_google_search_links(query)

all_links = set()

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(fetch_links, q) for q in queries]
    for future in as_completed(futures):
        try:
            links = future.result()
            all_links.update(links)
        except Exception as e:
            print(f"Error during search: {e}")

def load_site(url):
    content = site_loader.fetch_page_content(url)
    if content:
        print(f"Saved: {url}")
    else:
        print(f"Failed: {url}")


print(f"\nStarting to download {len(all_links)} unique links...\n")

with ThreadPoolExecutor(max_workers=10) as executor:
    list(executor.map(load_site, all_links))
