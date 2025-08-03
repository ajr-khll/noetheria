def format_llm_prompt(session):
    def clean_text_for_search(text):
        """Remove JSON formatting and special characters that might confuse search query generation"""
        if not text:
            return text
        # Remove common JSON characters and normalize spacing
        import re
        text = re.sub(r'[{}[\]"]', '', text)  # Remove braces, brackets, quotes
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        return text.strip()
    
    prompt = f"Initial question: {clean_text_for_search(session.initial_question)}\n\n"
    for followup in sorted(session.followups, key=lambda f: f.order):
        clean_question = clean_text_for_search(followup.question)
        clean_answer = clean_text_for_search(followup.answer) if followup.answer else '[Not answered yet]'
        prompt += f"Follow-up question: {clean_question}\n"
        prompt += f"Answer: {clean_answer}\n\n"
    return prompt
