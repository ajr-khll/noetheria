from openai import OpenAI
from dotenv import load_dotenv
import os
import sys

load_dotenv()

client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

stream = client.responses.create(
    model="gpt-4.1",
    input=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'double bubble bath' ten times fast."}
    ],
    stream=True,
)

for event in stream:
    if event.type == "response.output_text.delta":
        sys.stdout.write(event.delta)
        sys.stdout.flush()
        