# search_api.py
import requests

def brave_search(query, api_key, count=10):
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    params = {
        "q": query,
        "count": count,
        "freshness": "month"  # adjust as needed: day, week, month
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        results = response.json().get("web", {}).get("results", [])
        return [r["url"] for r in results]
    except Exception as e:
        print(f"[!] Brave Search Error: {e}")
        return []