# code_summarizer/graph_generator_ast.py

import ast
import networkx as nx
import matplotlib.pyplot as plt

class DependencyGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.graph = nx.DiGraph()
        self.current_scope = []

    def visit_FunctionDef(self, node):
        self.current_scope.append(node.name)
        self.graph.add_node(node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_ClassDef(self, node):
        self.current_scope.append(node.name)
        self.graph.add_node(node.name, node_color='lightgreen')
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.graph.add_edge(base.id, node.name)
        self.generic_visit(node)
        self.current_scope.pop()

    def visit_Call(self, node):
        if self.current_scope:
            caller = self.current_scope[-1]
            callee = ""
            if isinstance(node.func, ast.Name):
                callee = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee = node.func.attr
            if callee:
                self.graph.add_edge(caller, callee)
        self.generic_visit(node)

def build_dependency_graph_from_code(source_code):
    tree = ast.parse(source_code)
    builder = DependencyGraphBuilder()
    builder.visit(tree)
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(builder.graph, seed=42)
    nx.draw(builder.graph, pos, with_labels=True, node_color='skyblue', 
            edge_color='gray', node_size=2500, font_size=10, ax=ax,
            arrows=True, arrowstyle='->', arrowsize=20)
    return fig