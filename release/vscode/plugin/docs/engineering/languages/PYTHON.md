# Canonical AgentGuard Python SDK & Runtime Integration Guide

> **Language:** Python 3.9+  
> **Package:** `agentguard`  
> **Dependencies:** Zero external dependencies (Python Standard Library)  

---

## 1. Overview & Setup

The Python runtime is the native implementation of the AgentGuard Quad-Graph Substrate. It provides high-performance, in-process ACID graph operations, dynamic zero-prompt-tax prompt synthesis, pre-execution security gating, and execution trace logging.

### Installation
```bash
pip install agentguard
# or editable local mode
pip install -e .
```

---

## 2. Core Python API Reference

### A. Graph Engine Initialization (`AgentGraph` / `AgentGuardGraph`)

```python
from pathlib import Path
from agentguard import AgentGraph

# Option 1: Initialize workspace (.agentguard/, AGENTS.md, git hooks) & sync substrate
graph = AgentGraph.init(workspace_dir=".", no_hooks=False)

# Option 2: Load existing Quad-Graph substrate from SQLite
db_path = Path(".agentguard/graph.db")
graph = AgentGraph(db_path=db_path)
if db_path.exists():
    graph.load_from_db()
```

### B. Dynamic System Prompt Synthesis (`PromptSynthesizer`)

Synthesizes a minimal, role-tailored system prompt containing only active governing rules and authorized tool signatures:

```python
from agentguard.prompt.synthesizer import PromptSynthesizer

# Synthesize prompt for developer role
prompt = PromptSynthesizer.synthesize_prompt(
    graph=graph,
    role_id="developer",
    scope="root"  # optional subsystem scope
)

print(prompt)
```

### C. Pre-Execution Security Gate (`SecurityGate`)

Interceptor hook that enforces RBAC tool authorizations and logs execution traces to SQLite before runtime side effects occur:

```python
from agentguard.governance.gate import SecurityGate
from agentguard.core.models import RBACPermissionError

def safe_tool_executor(role_id: str, tool_name: str, tool_args: dict):
    try:
        # Enforce security gate
        SecurityGate.enforce_tool(
            graph=graph,
            role_id=role_id,
            tool_name=tool_name,
            actor_id="agent_worker_01",
            session_id="sess_8832"
        )
        # Execute tool logic if authorized
        return execute_action(tool_name, tool_args)
    except RBACPermissionError as err:
        print(f"[SECURITY ALERT] Security Gate Blocked Tool Call: {err}")
        raise
```

---

## 3. FastMCP / Model Context Protocol Integration

```python
from mcp.server.fastmcp import FastMCP
from agentguard.core.graph import AgentGuardGraph
from agentguard.governance.gate import SecurityGate

mcp_server = FastMCP("Governed-Python-Agent")
graph = AgentGuardGraph(db_path=".agentguard/graph.db")

@mcp_server.tool()
def update_code_file(role_id: str, target_file: str, content: str) -> str:
    """Modifies a code file with pre-execution security gating."""
    SecurityGate.enforce_tool(graph, role_id=role_id, tool_name="replace_file_content")
    
    with open(target_file, "w") as f:
        f.write(content)
    return f"Successfully updated {target_file}"
```
