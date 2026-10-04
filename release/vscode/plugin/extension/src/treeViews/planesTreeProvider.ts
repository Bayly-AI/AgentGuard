export class PlanesTreeProvider {
  private _onDidChangeTreeData: any;
  public readonly onDidChangeTreeData: any;
  private client: any;
  private vscode: any;

  constructor(client: any, vscode: any) {
    this.client = client;
    this.vscode = vscode;
    if (vscode?.EventEmitter) {
      this._onDidChangeTreeData = new vscode.EventEmitter();
      this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
  }

  public refresh(): void {
    if (this._onDidChangeTreeData) {
      this._onDidChangeTreeData.fire(undefined);
    }
  }

  public getTreeItem(element: any): any {
    return element;
  }

  public async getChildren(element?: any): Promise<any[]> {
    if (!this.vscode) return [];

    if (!element) {
      return [
        {
          label: "Agents & Roles Plane",
          collapsibleState: this.vscode.TreeItemCollapsibleState.Expanded,
          iconPath: new this.vscode.ThemeIcon("organization"),
          contextValue: "plane_agents",
          plane: "agents"
        },
        {
          label: "Invariants & Rules Plane",
          collapsibleState: this.vscode.TreeItemCollapsibleState.Expanded,
          iconPath: new this.vscode.ThemeIcon("shield"),
          contextValue: "plane_rules",
          plane: "rules"
        },
        {
          label: "Memory & Context Plane",
          collapsibleState: this.vscode.TreeItemCollapsibleState.Collapsed,
          iconPath: new this.vscode.ThemeIcon("database"),
          contextValue: "plane_memory",
          plane: "memory"
        },
        {
          label: "Code AST Plane",
          collapsibleState: this.vscode.TreeItemCollapsibleState.Collapsed,
          iconPath: new this.vscode.ThemeIcon("symbol-class"),
          contextValue: "plane_code",
          plane: "code"
        }
      ];
    }

    if (element.plane === "agents") {
      return [
        {
          label: "Role: Architect",
          description: "System topology & boundaries",
          iconPath: new this.vscode.ThemeIcon("person"),
          collapsibleState: this.vscode.TreeItemCollapsibleState.None
        },
        {
          label: "Role: Developer",
          description: "Autonomous code implementation",
          iconPath: new this.vscode.ThemeIcon("code"),
          collapsibleState: this.vscode.TreeItemCollapsibleState.None
        },
        {
          label: "Role: Reviewer",
          description: "Governance audit & DAG health",
          iconPath: new this.vscode.ThemeIcon("verified"),
          collapsibleState: this.vscode.TreeItemCollapsibleState.None
        }
      ];
    }

    if (element.plane === "rules") {
      return [
        {
          label: "GUARD-INV-001: Strict DAG Hierarchy",
          description: "Priority Tier 1 (Inviolable)",
          iconPath: new this.vscode.ThemeIcon("lock"),
          collapsibleState: this.vscode.TreeItemCollapsibleState.None
        },
        {
          label: "GUARD-INV-002: Zero External Core Dependencies",
          description: "Priority Tier 1 (Inviolable)",
          iconPath: new this.vscode.ThemeIcon("lock"),
          collapsibleState: this.vscode.TreeItemCollapsibleState.None
        },
        {
          label: "GUARD-DIR-003: Deterministic Gating",
          description: "Priority Tier 2 (Governing)",
          iconPath: new this.vscode.ThemeIcon("shield"),
          collapsibleState: this.vscode.TreeItemCollapsibleState.None
        }
      ];
    }

    if (element.plane === "memory") {
      return [
        {
          label: "Executive Blueprint",
          description: "docs/business/EXECUTIVE_BLUEPRINT.md",
          iconPath: new this.vscode.ThemeIcon("file-text"),
          collapsibleState: this.vscode.TreeItemCollapsibleState.None
        },
        {
          label: "Hath0r Compliance Spec",
          description: "docs/business/HATH0R_COMPLIANCE.md",
          iconPath: new this.vscode.ThemeIcon("file-text"),
          collapsibleState: this.vscode.TreeItemCollapsibleState.None
        }
      ];
    }

    return [];
  }
}
