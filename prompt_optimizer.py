from dotenv import load_dotenv
import os
import sys

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()

def prompt_optimization(unfiltered_prompt: str) -> str:
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = PromptTemplate.from_template(
        "Give me 4 google search queries I can make to fulfill this prompt:\n\n{unfiltered_prompt}"
    )
    response = llm.invoke(prompt.format(unfiltered_prompt=unfiltered_prompt))
    return response.content.strip()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        f = open(sys.argv[1], "r")
        unfiltered_prompt = f.read()
        f.close()
    else:
        # Default unfiltered prompt if none is provided 
        unfiltered_prompt = "Write a story about a hero."
    optimized_prompt = prompt_optimization(unfiltered_prompt)
    print(f"Optimized Prompt: {optimized_prompt}")
