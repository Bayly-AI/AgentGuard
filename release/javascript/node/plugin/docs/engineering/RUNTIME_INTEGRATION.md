# Developer Integration Guide: Python API & Security Gates

> **Module Name:** `agentguard`  
> **Target:** Agent Harness Developers, Framework Engineers, MCP Server Authors  

---

## 1. Quickstart Python Integration

Integrating AgentGuard into an agent execution loop requires two lines of code: one for dynamic zero-prompt-tax system prompt generation, and one for pre-tool execution security gating.

```python
from agentguard.core.graph import AgentGuardGraph
from agentguard.prompt.synthesizer import PromptSynthesizer
from agentguard.governance.gate import SecurityGate

# 1. Initialize or load Quad-Graph database
graph = AgentGuardGraph(db_path=".agentguard/graph.db")
graph.load_from_db()

# 2. Synthesize dynamic, zero-prompt-tax system prompt for active role
role_id = "developer"
system_prompt = PromptSynthesizer.synthesize_prompt(graph=graph, role_id=role_id)

print(system_prompt)
```

---

## 2. Pre-Tool Execution Security Gate

Before executing any tool requested by an LLM agent, wrap the dispatch call with `SecurityGate.enforce_tool()`. This guarantees 100% deterministic RBAC verification prior to runtime side effects.

```python
def execute_agent_tool_call(role_id: str, tool_name: str, tool_args: dict) -> dict:
    # Pre-execution RBAC Security Gate Check
    try:
        SecurityGate.enforce_tool(
            graph=graph,
            role_id=role_id,
            tool_name=tool_name,
            actor_id="agent_runner_v1",
            session_id="session_104"
        )
    except Exception as err:
        # Intercepted unauthorized tool call
        return {
            "status": "error",
            "error_type": "RBACPermissionError",
            "message": f"AgentGuard Security Gate Intercepted Execution: {err}"
        }

    # Dispatch tool execution safely
    return dispatch_tool_implementation(tool_name, tool_args)
```

---

## 3. Integrating with Model Context Protocol (MCP) Servers

When exposing tools via MCP servers, use AgentGuard to broker tool visibility and authorization:

```python
from mcp.server.fastmcp import FastMCP
from agentguard.core.graph import AgentGuardGraph
from agentguard.governance.gate import SecurityGate

mcp_server = FastMCP("Governed-Agent-Server")
graph = AgentGuardGraph(db_path=".agentguard/graph.db")

@mcp_server.tool()
def execute_database_query(role_id: str, query: str) -> str:
    """Execute SQL query safely guarded by AgentGuard."""
    # Pre-execution gate
    SecurityGate.enforce_tool(graph, role_id=role_id, tool_name="execute_database_query")

    # Run query logic
    return db_client.execute(query)


---

## 4. Canonical Language-Specific SDK Reference Guides

For complete code examples, middleware patterns, and client classes in your preferred programming language, see the canonical guides:

- 🐍 **[Python Integration Guide](languages/PYTHON.md)**: Native in-process package, `AgentGuardGraph`, `SecurityGate`, and FastMCP.
- 🟨 **[TypeScript / Node.js Integration Guide](languages/TYPESCRIPT.md)**: TypeScript client wrapper, Vercel AI SDK, and LangChain TS tool middleware.
- 🔷 **[Go Integration Guide](languages/GO.md)**: Golang IPC client wrapper and command process execution.
- ☕ **[Java / Kotlin Integration Guide](languages/JAVA.md)**: Spring Boot / Spring AI `AgentGuardClient` and ProcessBuilder IPC wrappers.
```
