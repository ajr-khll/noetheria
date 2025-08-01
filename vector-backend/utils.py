def format_llm_prompt(session):
    prompt = f"Initial question: {session.initial_question}\n\n"
    for followup in sorted(session.followups, key=lambda f: f.order):
        prompt += f"Follow-up question: {followup.question}\n"
        prompt += f"Answer: {followup.answer or '[Not answered yet]'}\n\n"
    return prompt
