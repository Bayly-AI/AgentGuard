# AgentGuard Model Context Protocol (MCP) & Claude Integration Guide

> **Integration Standard:** Model Context Protocol (MCP) Stdio JSON-RPC 2.0  
> **Supported Clients:** Claude Desktop, Claude Code CLI, Smithery, Cursor, Windsurf, FastMCP  

---

## 1. Executive Summary

AgentGuard provides a native **Model Context Protocol (MCP)** server (`agentguard mcp`), allowing **Anthropic Claude Desktop** and **Claude Code** to directly invoke non-bypassable RBAC security gates, dynamic zero-prompt-tax system prompts, Taguchi DoE optimization matrices, and FinOps token usage histograms.

---

## 2. Claude Desktop Integration (`claude_desktop_config.json`)

To register AgentGuard in **Claude Desktop**:

1. Open your Claude Desktop configuration file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the `agentguard` MCP server entry:

```json
{
  "mcpServers": {
    "agentguard": {
      "command": "agentguard",
      "args": ["mcp", "--dir", "/path/to/your/workspace"]
    }
  }
}
```

If using the standalone binary release directly:

```json
{
  "mcpServers": {
    "agentguard": {
      "command": "/usr/local/bin/agentguard",
      "args": ["mcp", "--dir", "/Users/username/Development/OpenSource/AgentGuard"]
    }
  }
}
```

---

## 3. Claude Code CLI Integration

To attach AgentGuard MCP tools to **Claude Code CLI**:

```bash
claude mcp add agentguard agentguard mcp --dir .
```

---

## 4. Exposed MCP Tool Surface

When connected to Claude Desktop or Claude Code, AgentGuard exposes 5 governed tools:

| MCP Tool Name | Function Purpose | Input Parameters |
| :--- | :--- | :--- |
| `agentguard_gate` | Pre-execution RBAC security gate verification | `role_id` (string), `tool_name` (string) |
| `agentguard_prompt` | Zero-prompt-tax system prompt synthesizer | `role_id` (string), `scope` (optional string) |
| `agentguard_taguchi` | Taguchi Robust Design & Orthogonal Arrays (L4..L18) | `array` (enum), `factors` (array), `snr_values` (array), `snr_type` (enum) |
| `agentguard_finops` | FinOps token usage analytics & ASCII histograms | `action` (record/histogram/check), `prompt` (string), `user_id` (string), `bins` (int) |
| `agentguard_quality_gate` | Full Hath0r 5-Gate compliance suite evaluation | `dir` (string) |

---

## 5. Publishing to MCP Registries (Smithery / Glama / PulseMCP)

AgentGuard is configured for instant 1-click deployment on public MCP registries:

- **Smithery.ai:** `smithery install agentguard`
- **Glama.ai:** Listed under Agent Security & FinOps Governance
- **PulseMCP:** Enterprise Security Gate & DoE Optimizer Category
