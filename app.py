# app.py (Final version with all 5 objectives, including AST Navigator)

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Import all the feature modules for your project
from code_summarizer.summarizer import summarize_large_code
from code_summarizer.search import semantic_code_search
from code_summarizer.graph_generator import build_dependency_graph_from_code
from code_summarizer.completer import complete_code_ai
# IMPORTANT: Importing your new AST-based navigation functions
from code_summarizer.navigator import extract_functions_and_calls, build_call_graph, graph_to_dot

# --- Page Configuration and Setup ---
st.set_page_config(page_title="AI Code Navigator", page_icon="🧭", layout="wide")
load_dotenv()

# --- Gemini Configuration ---
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except (TypeError, AttributeError):
    st.error("GEMINI_API_KEY not found. Please create a .env file and add your key.")
    st.stop()

# --- Main UI ---
st.title("AI-Powered Smart Code Base Navigator 🧭")
st.markdown("Select a feature below to begin analyzing your code.")

if "mode" not in st.session_state:
    st.session_state.mode = None

# --- Feature Selection Buttons for all 5 objectives ---
cols = st.columns(5)
if cols[0].button("📝 Code Summary", use_container_width=True): st.session_state.mode = "summarize"
if cols[1].button("🔍 Semantic Search", use_container_width=True): st.session_state.mode = "search"
if cols[2].button("📈 Dependency Graph", use_container_width=True): st.session_state.mode = "graph"
if cols[3].button("✍ Auto-Completion", use_container_width=True): st.session_state.mode = "complete"
if cols[4].button("🧭 Navigation", use_container_width=True): st.session_state.mode = "navigate" # <-- YOUR NAVIGATION BUTTON

st.markdown("---") # Visual separator

# --- Render UI based on the selected mode ---

# --- SUMMARIZE MODE ---
if st.session_state.mode == "summarize":
    st.subheader("Code Summarization")
    code_to_summarize = st.text_area("Paste code to summarize:", height=300, key="summarize_input")
    if st.button("Generate Summary", key="summarize_btn"):
        if code_to_summarize:
            with st.spinner("AI is analyzing and summarizing..."):
                summary = summarize_large_code(code_to_summarize)
                st.markdown("### Generated Summary")
                st.markdown(summary, unsafe_allow_html=True)

# --- SEARCH MODE ---
elif st.session_state.mode == "search":
    st.subheader("Semantic Code Search")
    code_to_search = st.text_area("Paste code to search within:", height=250, key="search_code_input")
    search_query = st.text_input("Ask a question about the code:", placeholder="e.g., What is the purpose of the 'is_prime' function?", key="search_query")
    if st.button("Search Code", key="search_btn"):
        if code_to_search and search_query:
            with st.spinner("Searching for the answer..."):
                result = semantic_code_search(code_to_search, search_query)
                st.markdown("### Answer")
                st.markdown(result, unsafe_allow_html=True)

# --- GRAPH MODE (using matplotlib) ---
elif st.session_state.mode == "graph":
    st.subheader("Code Dependency Graph")
    code_to_graph = st.text_area("Paste code to generate a graph from:", height=300, key="graph_input")
    if st.button("Generate Graph", key="graph_btn"):
        if code_to_graph:
            with st.spinner("Analyzing code and building graph..."):
                try:
                    graph_fig = build_dependency_graph_from_code(code_to_graph)
                    st.pyplot(graph_fig)
                except Exception as e:
                    st.error(f"Could not parse the code to build the graph: {e}")

# --- AUTO-COMPLETION MODE ---
elif st.session_state.mode == "complete":
    st.subheader("AI-Powered Code Completion")
    incomplete_code = st.text_area("Paste your incomplete code here:", height=300, key="complete_input", placeholder="def fibonacci(n):")
    if st.button("Complete Code", key="complete_btn"):
        if incomplete_code:
            with st.spinner("AI is completing your code..."):
                completed_code = complete_code_ai(incomplete_code)
                st.markdown("### AI-Completed Code")
                st.code(completed_code, language='python')

# --- NAVIGATION (AST-BASED) MODE ---
elif st.session_state.mode == "navigate":
    st.subheader("Code Navigation (AST Analysis)")
    code_to_navigate = st.text_area("Paste your COMPLETE code to navigate:", height=300, key="navigate_input")
    if st.button("Analyze and Navigate", key="navigate_btn"):
        if code_to_navigate:
            with st.spinner("Parsing code and building navigation map..."):
                try:
                    functions, calls = extract_functions_and_calls(code_to_navigate)
                    
                    if not functions:
                        st.warning("No functions were found in the provided code.")
                    else:
                        st.markdown("### Functions Found")
                        for func in functions:
                            with st.expander(f"Function: {func['name']} (Lines {func['lineno']}-{func['end_lineno']})"):
                                st.code(func['code'], language="python")

                        st.markdown("---")
                        st.markdown("### Call Graph")
                        call_graph = build_call_graph(calls)
                        dot_graph = graph_to_dot(call_graph)
                        st.graphviz_chart(dot_graph)
                        
                        st.markdown("---")
                        st.markdown("### Function Call Details")
                        for func_name, called_funcs in calls.items():
                            if called_funcs:
                                st.write(f"- Function **{func_name}** calls: {', '.join(called_funcs)}")
                            else:
                                st.write(f"- Function **{func_name}** makes no calls to other functions in this file.")

                except SyntaxError as e:
                    st.error(f"Syntax Error: Could not parse the code. Please provide valid Python code.\n\nDetails: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred during analysis: {e}")
        else:
            st.warning("Please paste some code to navigate.")