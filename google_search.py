import os 
import httpx 
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def google_search(api_key, search_engine_id, query, params):
    base_url = 'https://www.googleapis.com/customsearch/v1'
    final_params = {
        'key': api_key, 
        'cx': search_engine_id, 
        'q': query,
        **params
    }

    response = httpx.get(base_url, params=final_params)
    response.raise_for_status()
    return response.json()

api_key = os.getenv("CUSTOM_SEARCH_API")
search_engine_id = os.getenv("ENGINE_ID")
query = 'Python Tutorial'
search_results = []

for i in range(1, 100, 10):
    response = google_search(
        api_key=api_key,
        search_engine_id=search_engine_id,
        query=query,
        params={'start': i}
    )
    search_results.extend(response.get('items', []))

# Optional: convert to DataFrame and display top results
df = pd.DataFrame(search_results)
print(df[['title', 'link']].head())
