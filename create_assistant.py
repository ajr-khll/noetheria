from dotenv import load_dotenv
import os
import sys
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

with open("vector_store_id.txt", "r") as f:
    vector_store_id = f.read().strip()


assistant = openai.beta.assistants.create(
    name="Web Search Answer Bot",
    instructions="Answer the user's query by using as many different uploaded sources as possible. Cite multiple documents when relevant, and avoid relying solely on one file unless necessary.",
    tools=[{"type": "file_search"}],
    model="gpt-4o",
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
)

with open("assistant_id.txt", "w") as f:
    f.write(assistant.id)