# code_summarizer/ast_navigator.py

import ast
import networkx as nx

def extract_functions_and_calls(source_code):
    """
    Parses the source code using AST to find all functions and their calls.
    Returns a list of function metadata and a dictionary of calls.
    """
    tree = ast.parse(source_code)
    functions = []
    calls = {}

    # First pass: Collect all function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
            calls[node.name] = set()

    # Second pass: For each function, find the calls it makes
    class CallVisitor(ast.NodeVisitor):
        def __init__(self, current_func_name):
            self.current_func_name = current_func_name

        def visit_Call(self, call_node):
            if isinstance(call_node.func, ast.Name):
                # Ensure we don't add calls to functions not defined in the source
                if call_node.func.id in calls:
                    calls[self.current_func_name].add(call_node.func.id)
            self.generic_visit(call_node)

    for func_node in functions:
        visitor = CallVisitor(func_node.name)
        visitor.visit(func_node)

    # Prepare function metadata for the UI
    func_metadata = []
    for func_node in functions:
        # ast.get_source_segment is a reliable way to get the function's code
        source_segment = ast.get_source_segment(source_code, func_node)
        func_metadata.append({
            "name": func_node.name,
            "lineno": func_node.lineno,
            "end_lineno": func_node.end_lineno,
            "code": source_segment
        })

    return func_metadata, calls

def build_call_graph(calls):
    """
    Builds a networkx DiGraph from the calls dictionary.
    """
    G = nx.DiGraph()
    for caller, callees in calls.items():
        # Add the caller node even if it calls nothing
        G.add_node(caller)
        for callee in callees:
            G.add_edge(caller, callee)
    return G

def graph_to_dot(G):
    """
    Converts a networkx graph to the Graphviz DOT language format.
    """
    dot = "digraph G {\n"
    dot += '  rankdir="LR";\n'  # Left-to-right layout
    dot += '  node [shape=box, style="rounded,filled", fillcolor="skyblue"];\n'
    for node in G.nodes():
        dot += f'  "{node}";\n'
    for u, v in G.edges():
        dot += f'  "{u}" -> "{v}";\n'
    dot += "}"
    return dot