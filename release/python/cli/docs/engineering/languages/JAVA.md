# Canonical AgentGuard Java / Kotlin Integration Guide

> **Language:** Java 17+ / Kotlin  
> **Integration Pattern:** ProcessBuilder IPC / Spring AI Middleware  

---

## 1. Overview & Setup

Enterprise Java and Kotlin applications (Spring Boot, Spring AI, LangChain4j, Quarkus) integrate with AgentGuard using a process wrapper or native ProcessBuilder execution against the AgentGuard CLI binary.

---

## 2. Java AgentGuard Client Class

```java
package com.agentguard.sdk;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Path;

public class AgentGuardClient {
    private final String cliPath;
    private final String dbPath;

    public AgentGuardClient(String cliPath, String dbPath) {
        this.cliPath = cliPath != null ? cliPath : "agentguard";
        this.dbPath = dbPath != null ? dbPath : ".agentguard/graph.db";
    }

    public String synthesizePrompt(String roleId) throws Exception {
        ProcessBuilder pb = new ProcessBuilder(cliPath, "prompt", "--role", roleId, "--db", dbPath);
        Process process = pb.start();

        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            sb.append(line).append("\n");
        }

        if (process.waitFor() != 0) {
            throw new RuntimeException("Failed to synthesize prompt for role: " + roleId);
        }
        return sb.toString().trim();
    }

    public void enforceSecurityGate(String roleId, String toolName) throws Exception {
        ProcessBuilder pb = new ProcessBuilder(cliPath, "gate", "--role", roleId, "--tool", toolName, "--db", dbPath);
        Process process = pb.start();

        if (process.waitFor() != 0) {
            BufferedReader errReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = errReader.readLine()) != null) {
                sb.append(line);
            }
            throw new SecurityException("AgentGuard Security Gate DENIED: " + sb.toString());
        }
    }
}
```

---

## 3. Spring AI Middleware Example

```java
@Component
public class GovernedAgentService {

    @Autowired
    private AgentGuardClient agentGuard;

    public String runGovernedTask(String roleId, String toolName, Supplier<String> toolTask) throws Exception {
        // Enforce Security Gate before tool execution
        agentGuard.enforceSecurityGate(roleId, toolName);

        // Execute tool safely
        return toolTask.get();
    }
}
```
