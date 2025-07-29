from dotenv import load_dotenv
import os
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
from typing import List

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ResearchCompliance(BaseModel):
    research_required: bool
    follow_up: Optional[List[str]]
    basic_answer: Optional[str]
    word_count_mentioned: bool


def check_prompt(prompt):
    response = client.responses.parse(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": """Determine whether the prompt has significant depth and complexity that requires further research or follow-up questions. 
             If the prompt is basic, respond normally as a helpful assistant.
             If the prompt is complex, do not return a basic answer and provide follow-up questions to clarify the scope of research that needs to be done. Limit to 4 follow-up questions.
             If the word count is mentioned, indicate so."""},
            {"role": "user", "content": prompt}
        ],
        text_format=ResearchCompliance,
    )
    return response.output_parsed


if __name__ == "__main__":
    # Example usage
    print(check_prompt("Write a 1000 word essay on Nietzche and Fascism"))  # Example prompt to test the function