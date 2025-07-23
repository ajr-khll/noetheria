import openai
import os
import time
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def deep_research(query: str, assistant_id: str, vector_store_id: str) -> str:
    thread = openai.beta.threads.create()

    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )

    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status in ["completed", "failed"]:
            break
        time.sleep(1)

    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value if messages.data else "No response."
    return reply

with open("vector_store_id.txt", "r") as f:
    vector_store_id = f.read().strip()

assistant = openai.beta.assistants.create(
    name="Web Search Answer Bot",
    instructions="Answer questions using only the information in the attached vector store.",
    tools=[{"type": "file_search"}],
    model="gpt-4o",
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
)

if __name__ == "__main__":
    query = input("Enter your research query: ")
    result = deep_research(query, assistant.id, vector_store_id)
    print(f"\n📎 Research Result:\n{result}")