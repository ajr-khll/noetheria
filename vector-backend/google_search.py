import os
import httpx
import sys
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import urlparse
from cache_config import cache, CacheTypes

load_dotenv()

def fetch_google_search_links(query: str, num_results: int = 5) -> list:
    # Try cache first
    cache_key = f"{query}_{num_results}"
    cached_results = cache.get(CacheTypes.SEARCH_RESULTS, cache_key)
    if cached_results:
        print(f"[CACHE HIT] Using cached search results for: {query}")
        return cached_results

    api_key = os.getenv("CUSTOM_SEARCH_API")
    search_engine_id = os.getenv("ENGINE_ID")
    base_url = 'https://www.googleapis.com/customsearch/v1'
    BAD_DOMAINS = [
        "reddit.com", "amazon.com", "quora.com", "pinterest.com",
        "youtube.com", "facebook.com", "ebay.com"
    ]

    def is_valid(link: str) -> bool:
        try:
            domain = urlparse(link).netloc.lower()
            return not any(bad in domain for bad in BAD_DOMAINS)
        except:
            return False

    try:
        response = httpx.get(base_url, params={
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': num_results
        })
        response.raise_for_status()
        data = response.json()
        items = data.get('items', [])
        print(f"[API CALL] Fresh search results for '{query}'")

        links = [item.get("link") for item in items if item.get("link")]
        filtered_links = [link for link in links if is_valid(link)]
        
        # Cache the results for 24 hours
        cache.set(CacheTypes.SEARCH_RESULTS, cache_key, filtered_links, ttl_seconds=86400)
        print(f"[CACHE SET] Cached search results for: {query}")
        
        return filtered_links

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            print("Rate limit exceeded. Checking cache for fallback...")
            # Try to return stale cache as fallback
            stale_results = cache.get(CacheTypes.SEARCH_RESULTS, cache_key)
            if stale_results:
                print(f"[CACHE FALLBACK] Using stale cache for: {query}")
                return stale_results
            print("No cached results available.")
        else:
            raise

    return []



if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Write a story about a hero."
    print(f"Fetching links for query: {query}")
    links = fetch_google_search_links(query)
    print(links if links else ["No results found."])
