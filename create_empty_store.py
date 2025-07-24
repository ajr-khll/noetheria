from dotenv import load_dotenv
import os
import openai


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

vector_store = openai.vector_stores.create(
    name="MyWebScrapeStore"
)

with open("vector_store_id.txt", "w") as f:
    f.write(vector_store.id)
f.close()