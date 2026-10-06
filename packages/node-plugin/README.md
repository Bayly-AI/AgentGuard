# @agentguard/node-plugin: AgentGuard Node.js Plugin & SDK

[![npm version](https://img.shields.io/badge/npm-1.0.0-blue.svg)](#)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-8%2F8%20passing-brightgreen.svg)](#)

> **@agentguard/node-plugin** provides canonical Node.js and TypeScript bindings for the **AgentGuard Standalone Cognitive Substrate & Governance Control Plane**. Seamlessly integrate zero-prompt-tax prompt synthesis, pre-execution security gating, and Hath0r Quality Gates into your JavaScript and TypeScript agentic systems (LangChain JS, Vercel AI SDK, LlamaIndex TS, Fastify/Express, and Model Context Protocol servers).

---

## ⚡ Quickstart

### Installation

```bash
npm install @agentguard/node-plugin
```

### Basic Usage Example

```typescript
import { AgentGuardPlugin } from "@agentguard/node-plugin";

const plugin = new AgentGuardPlugin();

// 1. Synthesize zero-prompt-tax system prompt for active agent role
const systemPrompt = await plugin.client.synthesizePrompt("developer");
console.log("Synthesized System Prompt:\n", systemPrompt);

// 2. Wrap tool call with pre-execution Security Gate
const fileContent = await plugin.wrapTool("developer", "view_file", async () => {
  return "Controlled content read from disk";
});

// 3. Unauthorized tool calls are intercepted immediately!
try {
  await plugin.wrapTool("reviewer", "replace_file_content", async () => {
    return "Will be blocked";
  });
} catch (err) {
  console.error("AgentGuard Intercepted Tool Execution:", err.message);
  // [AgentGuard DENIED] Role 'reviewer' cannot execute tool 'replace_file_content'
}
```

---

## 🛡️ Express / Connect HTTP Middleware

Gating HTTP endpoints or REST agent worker gateways:

```typescript
import express from "express";
import { AgentGuardPlugin } from "@agentguard/node-plugin";

const app = express();
const plugin = new AgentGuardPlugin();

app.use(express.json());

// Protect API endpoints with AgentGuard Security Gate middleware
app.post("/api/tools/:toolName", plugin.expressGateMiddleware(), (req, res) => {
  res.json({ status: "success", message: `Tool ${req.params.toolName} executed safely.` });
});

app.listen(3000, () => console.log("Governed Express Agent Gateway listening on port 3000"));
```

---

## 🧪 Testing

Run the native Node.js test suite:

```bash
npm test
```

All 8 core tests run in under 2 seconds:
- Workspace Initialization (`init`)
- Zero-Prompt-Tax System Prompt Synthesis
- Security Gate Authorizations (`view_file` PASSED, `replace_file_content` DENIED)
- Function Wrapping (`wrapTool`)
- Graph Substrate & Priority Tier DAG Validation
- Hath0r Quality Gates Suite Evaluation

---

## 📚 Complete API & Language Documentation

- **[API Reference Guide](API_REFERENCE.md)**
- **[Parent AgentGuard Repository](https://github.com/Bayly-AI/AgentGuard)**
