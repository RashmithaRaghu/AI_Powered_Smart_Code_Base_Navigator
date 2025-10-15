# code_summarizer/summarizer.py

import streamlit as st
import google.generativeai as genai

def chunk_code(code, max_tokens=15000):
    """Splits large code into smaller chunks."""
    lines = code.splitlines()
    chunks, current_chunk, current_length = [], [], 0
    for line in lines:
        line_length = len(line) // 4
        if current_length + line_length > max_tokens:
            chunks.append('\n'.join(current_chunk))
            current_chunk, current_length = [line], line_length
        else:
            current_chunk.append(line)
            current_length += line_length
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    return chunks

def summarize_chunk(code_chunk, is_partial=False, model_name="models/gemini-pro-latest"):
    """Summarizes a single piece of code using Gemini."""
    context = "This is a partial chunk from a larger codebase." if is_partial else "This is a complete script."
    prompt = f"""
    As an expert software developer, provide a detailed explanation for the following Python code.
    {context}
    Analyze its purpose, key functions, classes, overall logic, and control flow.
    Explain what the code is trying to achieve in a clear and concise manner.
    Format your output using Markdown for clear readability.

    Code:
    ```python
    {code_chunk}
    ```
    """
    model_client = genai.GenerativeModel(model_name)
    response = model_client.generate_content(prompt)
    return response.text.strip()

def summarize_large_code(code, model_name="models/gemini-pro-latest"):
    """Orchestrates the summarization of large code by chunking."""
    chunks = chunk_code(code)
    if len(chunks) == 1:
        return summarize_chunk(chunks[0], is_partial=False, model_name=model_name)

    st.info(f"Code is large. Splitting into {len(chunks)} chunks for analysis...")
    chunk_summaries = []
    
    progress_bar = st.progress(0, text="Summarizing chunks...")
    for i, chunk in enumerate(chunks, 1):
        summary = summarize_chunk(chunk, is_partial=True, model_name=model_name)
        chunk_summaries.append(summary)
        progress_bar.progress(i / len(chunks), text=f"Summarizing chunk {i}/{len(chunks)}")

    progress_bar.progress(1.0, text="Combining summaries...")
    combined_summary = "\n\n---\n\n".join(chunk_summaries)
    final_prompt = f"""
    You are an expert code analyst. Synthesize the following partial summaries into one
    final, cohesive, and comprehensive explanation of the entire codebase.
    Focus on Overall Architecture, Key Components, and Execution Flow.
    Ensure the final output is well-structured and easy to read using Markdown.
    
    Partial Summaries:
    ---
    {combined_summary}
    ---
    """
    model_client = genai.GenerativeModel(model_name)
    response = model_client.generate_content(final_prompt)
    progress_bar.empty()
    return response.text.strip()