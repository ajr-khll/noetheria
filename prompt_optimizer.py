from dotenv import load_dotenv
import os
import sys

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()

def prompt_optimization(unfiltered_prompt: str) -> str:
    llm = ChatOpenAI(
        model="gpt-4.1",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = PromptTemplate.from_template(
        """Give me 4 google search queries I can make to fulfill this prompt:\n\n{unfiltered_prompt}
        The queries should be relevant to the prompt and should help in gathering information or resources related to it.
        The queries should be returned with newlines between them, with no other text.
        The queries should be specific and detailed, and should not be too short or too long."""
    )
    response = llm.invoke(prompt.format(unfiltered_prompt=unfiltered_prompt))
    return response.content.strip()

if __name__ == "__main__":
    pass
