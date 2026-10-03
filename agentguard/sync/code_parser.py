"""AST Code Parser for Python source code ingestion into KnowledgeGraph."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Tuple

from agentguard.core.models import AgentGraphEdge, AgentGraphNode, AgentGraphPlane


class CodeASTParser:
    """Parses Python source files into KnowledgeGraph AST nodes and relational edges."""

    @staticmethod
    def parse_python_file(file_path: Path) -> Tuple[List[AgentGraphNode], List[AgentGraphEdge]]:
        """Extract classes, functions, docstrings, and imports from a Python file."""
        if not file_path.exists():
            return [], []

        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError:
            return [], []

        nodes: List[AgentGraphNode] = []
        edges: List[AgentGraphEdge] = []

        mod_id = f"ast:module:{file_path.stem}"
        docstring = ast.get_docstring(tree) or ""

        mod_node = AgentGraphNode(
            id=mod_id,
            plane=AgentGraphPlane.KNOWLEDGE.value,
            type="code_module",
            label=f"Module {file_path.name}",
            content=f"Python Module: {file_path.name}\nDocstring: {docstring}",
            properties={"file_path": str(file_path)}
        )
        nodes.append(mod_node)

        for stmt in tree.body:
            if isinstance(stmt, ast.ClassDef):
                cls_id = f"ast:class:{file_path.stem}:{stmt.name}"
                cls_doc = ast.get_docstring(stmt) or ""
                cls_node = AgentGraphNode(
                    id=cls_id,
                    plane=AgentGraphPlane.KNOWLEDGE.value,
                    type="code_class",
                    label=f"Class {stmt.name}",
                    content=f"Class {stmt.name} in {file_path.name}\nDocstring: {cls_doc}",
                    properties={"file_path": str(file_path), "class_name": stmt.name}
                )
                nodes.append(cls_node)
                edges.append(AgentGraphEdge(
                    source=mod_id,
                    target=cls_id,
                    relation="CONTAINS_CLASS",
                    plane=AgentGraphPlane.KNOWLEDGE.value
                ))

                # Base classes inheritance edges
                for base in stmt.bases:
                    if isinstance(base, ast.Name):
                        edges.append(AgentGraphEdge(
                            source=cls_id,
                            target=f"ast:class_ref:{base.id}",
                            relation="INHERITS_FROM",
                            plane=AgentGraphPlane.KNOWLEDGE.value
                        ))

                # Parse methods inside class
                for m_stmt in stmt.body:
                    if isinstance(m_stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_id = f"ast:func:{file_path.stem}:{stmt.name}.{m_stmt.name}"
                        m_doc = ast.get_docstring(m_stmt) or ""
                        m_node = AgentGraphNode(
                            id=m_id,
                            plane=AgentGraphPlane.KNOWLEDGE.value,
                            type="code_function",
                            label=f"{stmt.name}.{m_stmt.name}",
                            content=f"Method {m_stmt.name} of class {stmt.name} in {file_path.name}\nDocstring: {m_doc}",
                            properties={"file_path": str(file_path), "class_name": stmt.name, "func_name": m_stmt.name}
                        )
                        nodes.append(m_node)
                        edges.append(AgentGraphEdge(
                            source=cls_id,
                            target=m_id,
                            relation="CONTAINS_METHOD",
                            plane=AgentGraphPlane.KNOWLEDGE.value
                        ))

            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_id = f"ast:func:{file_path.stem}:{stmt.name}"
                fn_doc = ast.get_docstring(stmt) or ""
                fn_node = AgentGraphNode(
                    id=fn_id,
                    plane=AgentGraphPlane.KNOWLEDGE.value,
                    type="code_function",
                    label=f"Function {stmt.name}",
                    content=f"Function {stmt.name} in {file_path.name}\nDocstring: {fn_doc}",
                    properties={"file_path": str(file_path), "func_name": stmt.name}
                )
                nodes.append(fn_node)
                edges.append(AgentGraphEdge(
                    source=mod_id,
                    target=fn_id,
                    relation="CONTAINS_FUNCTION",
                    plane=AgentGraphPlane.KNOWLEDGE.value
                ))

        return nodes, edges
