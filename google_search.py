import os
import httpx
import sys
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def fetch_google_search_links(query: str, num_results: int = 10) -> list:
    api_key = os.getenv("CUSTOM_SEARCH_API")
    search_engine_id = os.getenv("ENGINE_ID")
    base_url = 'https://www.googleapis.com/customsearch/v1'
    search_results = []

    for i in range(1, num_results, 10):
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'start': i
        }
        try:
            response = httpx.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            search_results.extend(data.get('items', []))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print("Rate limit exceeded. Try again later.")
                break
            else:
                raise

    if not search_results:
        return []
    df = pd.DataFrame(search_results)
    return df['link'].tolist() if 'link' in df.columns else []


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Write a story about a hero."
    print(f"Fetching links for query: {query}")
    links = fetch_google_search_links(query)
    print(links if links else ["No results found."])
