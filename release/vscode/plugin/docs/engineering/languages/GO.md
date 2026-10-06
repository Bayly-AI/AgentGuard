# Canonical AgentGuard Go Integration Guide

> **Language:** Go (1.20+)  
> **Integration Pattern:** Exec Command IPC / Direct SQLite Substrate Query  

---

## 1. Overview & Setup

Go microservices and agent harnesses interface with AgentGuard using zero-memory overhead sub-process command invocation or embedded CGO SQLite drivers against `.agentguard/graph.db`.

---

## 2. Go AgentGuard SDK Wrapper

```go
package agentguard

import (
	"bytes"
	"fmt"
	"os/exec"
	"strings"
)

type Client struct {
	CLIPath string
	DBPath  string
}

func NewClient(cliPath, dbPath string) *Client {
	if cliPath == "" {
		cliPath = "agentguard"
	}
	if dbPath == "" {
		dbPath = ".agentguard/graph.db"
	}
	return &Client{CLIPath: cliPath, DBPath: dbPath}
}

// SynthesizePrompt fetches dynamic zero-prompt-tax system prompt
func (c *Client) SynthesizePrompt(roleID string) (string, error) {
	cmd := exec.Command(c.CLIPath, "prompt", "--role", roleID, "--db", c.DBPath)
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		return "", fmt.Errorf("failed to synthesize prompt: %w", err)
	}
	return strings.TrimSpace(out.String()), nil
}

// EnforceSecurityGate verifies pre-execution tool authorization
func (c *Client) EnforceSecurityGate(roleID, toolName string) error {
	cmd := exec.Command(c.CLIPath, "gate", "--role", roleID, "--tool", toolName, "--db", c.DBPath)
	var stderr bytes.Buffer
	cmd.Stderr = &stderr
	err := cmd.Run()
	if err != nil {
		return fmt.Errorf("security gate DENIED: %s", stderr.String())
	}
	return nil
}
```

---

## 3. Go Tool Middleware Usage

```go
package main

import (
	"fmt"
	"log"

	"myproject/agentguard"
)

func main() {
	client := agentguard.NewClient("agentguard", ".agentguard/graph.db")

	// Pre-execution Security Gate check
	err := client.EnforceSecurityGate("developer", "view_file")
	if err != nil {
		log.Fatalf("Action blocked: %v", err)
	}

	fmt.Println("Security Gate PASSED: Executing view_file...")
}
```
