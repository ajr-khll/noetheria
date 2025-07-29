from dotenv import load_dotenv
import os
import openai  # Using the standard OpenAI library

load_dotenv()

def prompt_optimization(unfiltered_prompt: str, follow_ups: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    system_prompt = (
        "You are an assistant that generates 4 specific Google search queries "
        "that help someone fulfill an information need based on a user prompt, as well as a json of follow-up questions and answers "
        "The queries should be:\n"
        "- Relevant to the prompt\n"
        "- Focused on helping gather information or resources\n"
        "- Returned with no extra text, just one query per line\n"
        "- Specific and detailed, not too short or vague"
    )

    user_prompt = f"Give me 4 Google search queries for this prompt:\n\n{unfiltered_prompt}\n\n\nFollow-up questions and answers:\n\n{follow_ups}"

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5
    )

    return response.choices[0].message["content"].strip()

if __name__ == "__main__":
    test_input = "How can I build a low-cost hydroponics system at home?"
    print(prompt_optimization(test_input))
