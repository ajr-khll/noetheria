import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse
from cache_config import cache, CacheTypes
from custom_search_algorithm.api.search_api import brave_search
from custom_search_algorithm.core.crawler import crawl_pages
from custom_search_algorithm.core.graph_builder import build_graph
from custom_search_algorithm.core.priority_queue import PriorityQueue

load_dotenv()

def fetch_google_search_links(query: str, num_results: int = 5) -> list:
    # Try cache first
    cache_key = f"{query}_{num_results}"
    cached_results = cache.get(CacheTypes.SEARCH_RESULTS, cache_key)
    if cached_results:
        print(f"[CACHE HIT] Using cached search results for: {query}")
        return cached_results

    brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not brave_api_key:
        print("Warning: BRAVE_API_KEY not found, falling back to empty results")
        return []

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
        print(f"[API CALL] Fetching search results for '{query}' using custom algorithm")
        
        # Step 1: Get initial search results from Brave
        urls = brave_search(query, brave_api_key, count=min(num_results * 2, 20))
        if not urls:
            print("No search results found from Brave API")
            return []
        
        # Filter out bad domains
        filtered_urls = [url for url in urls if is_valid(url)]
        if not filtered_urls:
            print("All URLs filtered out due to domain restrictions")
            return []
        
        # Step 2: Crawl and parse the pages
        print(f"[CRAWLING] Processing {len(filtered_urls)} URLs")
        parsed_pages = crawl_pages(filtered_urls, max_workers=5)
        
        if not parsed_pages:
            print("No pages could be crawled successfully")
            return filtered_urls[:num_results]
        
        # Step 3: Build semantic graph and rank results
        print(f"[RANKING] Building semantic graph for {len(parsed_pages)} pages")
        graph = build_graph(parsed_pages, query)
        
        # Step 4: Use priority queue to get best results
        pq = PriorityQueue()
        for url in graph.nodes:
            score = graph.nodes[url]['score']
            pq.push(score, url)
        
        # Extract top results
        ranked_results = []
        for _ in range(min(num_results, len(graph.nodes))):
            url = pq.pop()
            if url:
                ranked_results.append(url)
        
        # If we don't have enough ranked results, fill with remaining filtered URLs
        if len(ranked_results) < num_results:
            remaining_urls = [url for url in filtered_urls if url not in ranked_results]
            ranked_results.extend(remaining_urls[:num_results - len(ranked_results)])
        
        final_results = ranked_results[:num_results]
        
        # Cache the results for 24 hours
        cache.set(CacheTypes.SEARCH_RESULTS, cache_key, final_results, ttl_seconds=86400)
        print(f"[CACHE SET] Cached {len(final_results)} search results for: {query}")
        
        return final_results

    except Exception as e:
        print(f"Error in custom search algorithm: {e}")
        print("Checking cache for fallback...")
        # Try to return stale cache as fallback
        stale_results = cache.get(CacheTypes.SEARCH_RESULTS, cache_key)
        if stale_results:
            print(f"[CACHE FALLBACK] Using stale cache for: {query}")
            return stale_results
        print("No cached results available.")
        return []



if __name__ == "__main__":
    raw_query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Write a story about a hero."
    # Clean the query: remove extra quotes, newlines, and normalize whitespace
    query = raw_query.replace('"', '').replace('\n', ' ').strip()
    # Normalize multiple spaces to single spaces
    query = ' '.join(query.split())
    print(f"Fetching links for query: {query}")
    links = fetch_google_search_links(query)
    print(links if links else ["No results found."])
