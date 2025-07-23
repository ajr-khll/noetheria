import openai
import os
from dotenv import load_dotenv
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

# Step 1: Upload the file to OpenAI
file = openai.files.create(
    file=open("information.jsonl", "rb"),
    purpose="assistants"
)

# Step 2: Create a vector store using the uploaded file
vector_store = openai.beta.vector_stores.create(
    name="MyWebScrapeStore",
    file_ids=[file.id]
)

with open("vector_store_id.txt", "w") as f:
    f.write(vector_store.id)
f.close()