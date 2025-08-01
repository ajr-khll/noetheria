from dotenv import load_dotenv
import os
from openai import OpenAI  # New SDK

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def prompt_optimization(unfiltered_prompt: str) -> str:
    system_prompt = (
        "You are an assistant that generates 4 specific Google search queries "
        "that help someone fulfill an information need based on a user prompt, as well as a JSON of follow-up questions and answers. "
        "The queries should be:\n"
        "- Relevant to the prompt\n"
        "- Focused on helping gather information or resources\n"
        "- Returned with no extra text, just one query per line\n"
        "- Specific and detailed, not too short or vague"
    )

    user_prompt = f"Give me 4 Google search queries for this prompt which includes follow-up questions and answers for clarification. Do not number or quote them. Just the queries.:\n\n{unfiltered_prompt}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    test_input = "How can I build a low-cost hydroponics system at home?"
    print(prompt_optimization(test_input))
