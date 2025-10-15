# code_summarizer/search.py

import streamlit as st
import google.generativeai as genai

def semantic_code_search(code, query, model_name="models/gemini-pro-latest"):
    """
    Performs a semantic search on the code based on a natural language query.
    """
    st.info("Performing semantic search...")

    prompt = f"""
    You are an expert code assistant. Your task is to answer a question about the
    following code snippet. Base your answer STRICTLY on the provided code.

    Do not answer if the code does not contain the information.
    First, provide a direct, natural language answer to the question.
    Then, if relevant, show the specific line(s) of code that support your answer.

    ---
    CODE CONTEXT:
    ```python
    {code}
    ```
    ---
    USER'S QUESTION:
    "{query}"
    ---
    
    ANSWER:
    """

    model_client = genai.GenerativeModel(model_name)
    response = model_client.generate_content(prompt)
    return response.text.strip()