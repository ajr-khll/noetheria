import openai
from openai import OpenAI
import os
import time
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from typing_extensions import override
from openai import AssistantEventHandler
 
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.
 
class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)

client = OpenAI()

def deep_research(query: str, assistant_id: str, vector_store_id: str) -> str:
    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions="Answer questions using only the information in the attached vector store.",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value if messages.data else "No response."
    return reply


with open("vector_store_id.txt", "r") as f:
    vector_store_id = f.read().strip()
f.close()

with open("assistant_id.txt", "r") as f:
    assistant_id = f.read().strip()
f.close()


if __name__ == "__main__":
    query = input("Enter your query: ")
    print("\nSearching for information...\n")
    response = deep_research(query, assistant_id, vector_store_id)
    print(f"\nResponse:\n{response}")