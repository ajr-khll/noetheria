import openai
from openai import OpenAI
import os
import time
from dotenv import load_dotenv
from typing import override
from openai import AssistantEventHandler


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")



client = OpenAI()

def run_deep_research(prompt: str, assistant_id: str):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    def stream_response():
        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant_id,
        ) as stream:
            for event in stream:
                if event.event == "thread.message.delta":
                    delta = event.data.delta
                    if (delta.content and 
                        len(delta.content) > 0 and 
                        hasattr(delta.content[0], 'text') and 
                        delta.content[0].text and 
                        hasattr(delta.content[0].text, 'value') and 
                        delta.content[0].text.value):
                        yield delta.content[0].text.value

    return thread.id, stream_response()



with open("vector_store_id.txt", "r") as f:
    vector_store_id = f.read().strip()
f.close()

with open("assistant_id.txt", "r") as f:
    assistant_id = f.read().strip()
f.close()

if __name__ == "__main__":
    query = input("Enter your query: ")
    print("\nSearching for information...\n")
    thread_id, response_stream = run_deep_research(query, assistant_id)
    response = ""
    for chunk in response_stream:
        response += chunk
    print(f"\nResponse:\n{response}")