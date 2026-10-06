export class GatesTreeProvider {
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

    return [
      {
        label: "Architect RBAC Policy",
        description: "view_file, route, validate (ReadOnly)",
        iconPath: new this.vscode.ThemeIcon("check"),
        collapsibleState: this.vscode.TreeItemCollapsibleState.None
      },
      {
        label: "Developer RBAC Policy",
        description: "write_to_file, replace_file_content, run_command",
        iconPath: new this.vscode.ThemeIcon("check"),
        collapsibleState: this.vscode.TreeItemCollapsibleState.None
      },
      {
        label: "Reviewer RBAC Policy",
        description: "view_file, validate, quality-gate (Strict ReadOnly)",
        iconPath: new this.vscode.ThemeIcon("shield"),
        collapsibleState: this.vscode.TreeItemCollapsibleState.None
      },
      {
        label: "Policy Boundary Check",
        description: "100% Deterministic (Zero Drift)",
        iconPath: new this.vscode.ThemeIcon("verified"),
        collapsibleState: this.vscode.TreeItemCollapsibleState.None
      }
    ];
  }
}
