# code_summarizer/completer.py

import streamlit as st
import google.generativeai as genai

def complete_code_ai(incomplete_code, model_name="models/gemini-pro-latest"):
    """
    Uses the Gemini model to intelligently complete a piece of code.
    """
    st.info("AI is generating your code completion...")

    prompt = f"""
    You are an expert Python code completion assistant.
    The user has provided the following incomplete Python code. Your task is to
    complete it in a logical and helpful way. Make sure the final code is runnable
    and follows best practices.

    Return only the completed, raw Python code inside a single code block. 
    Do not add any explanations, introductory text, or markdown formatting like ```python.

    INCOMPLETE CODE:
    ---
    {incomplete_code}
    ---

    COMPLETED CODE:
    """
    
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    
    # Clean up the response to get only the code, removing markdown wrappers
    completed_code = response.text.strip()
    if completed_code.startswith("```python"):
        completed_code = completed_code[9:]
    if completed_code.startswith("```"):
        completed_code = completed_code[3:]
    if completed_code.endswith("```"):
        completed_code = completed_code[:-3]
        
    return completed_code.strip()