export class QuadGraphWebviewPanel {
  public static currentPanel: QuadGraphWebviewPanel | undefined;
  private readonly panel: any;
  private readonly client: any;

  private constructor(panel: any, client: any) {
    this.panel = panel;
    this.client = client;
    this.update();
    this.panel.onDidDispose(() => this.dispose(), null, []);
  }

  public static createOrShow(vscode: any, client: any) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    if (QuadGraphWebviewPanel.currentPanel) {
      QuadGraphWebviewPanel.currentPanel.panel.reveal(column);
      QuadGraphWebviewPanel.currentPanel.update();
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      "agentguardQuadGraph",
      "AgentGuard: Quad-Graph Architecture",
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true
      }
    );

    QuadGraphWebviewPanel.currentPanel = new QuadGraphWebviewPanel(panel, client);
  }

  public async update() {
    this.panel.webview.html = this.getHtmlForWebview();
  }

  public dispose() {
    QuadGraphWebviewPanel.currentPanel = undefined;
    this.panel.dispose();
  }

  private getHtmlForWebview(): string {
    const mermaidSrc = `
flowchart TD
    subgraph INVARIANTS [Tier 1: Inviolable Invariants]
        INV1["GUARD-INV-001: Strict DAG Hierarchy"]
        INV2["GUARD-INV-002: Zero External Dependencies"]
    end

    subgraph AGENTS [Agents & Roles]
        A1["Role: Architect"]
        A2["Role: Developer"]
        A3["Role: Reviewer"]
    end

    subgraph GATES [RBAC Tool Security Gates]
        G1["ReadOnly Gate (view_file, route)"]
        G2["Full Engineering Gate (write, replace, run)"]
        G3["Verification Gate (validate, quality-gate)"]
    end

    subgraph MEMORY [Memory & Context]
        M1["Executive Blueprint"]
        M2["Hath0r Compliance Spec"]
    end

    INV1 -.->|GOVERNS| A1
    INV1 -.->|GOVERNS| A2
    INV1 -.->|GOVERNS| A3
    A1 -->|AUTHORIZED_FOR| G1
    A2 -->|AUTHORIZED_FOR| G2
    A3 -->|AUTHORIZED_FOR| G3
    A1 -.->|REFERENCES| M1
    `;

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AgentGuard Quad-Graph Substrate</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: var(--vscode-editor-background); color: var(--vscode-editor-foreground); padding: 16px; margin: 0; }
    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--vscode-widget-border); padding-bottom: 12px; margin-bottom: 16px; }
    .title { font-size: 1.2rem; font-weight: 600; color: #0284c7; }
    .canvas { background: var(--vscode-editor-background); padding: 20px; border-radius: 8px; border: 1px solid var(--vscode-widget-border); }
  </style>
</head>
<body>
  <div class="header">
    <div class="title">🛡️ AgentGuard Quad-Graph Architecture & Security Gates</div>
  </div>
  <div class="canvas">
    <pre class="mermaid">${mermaidSrc}</pre>
  </div>
  <script>
    mermaid.initialize({ startOnLoad: true, theme: 'dark' });
  </script>
</body>
</html>`;
  }
}
