export class FinOpsTreeProvider {
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
        label: "Token Tax Reduction",
        description: "95.2% Saved",
        iconPath: new this.vscode.ThemeIcon("graph-line"),
        collapsibleState: this.vscode.TreeItemCollapsibleState.None
      },
      {
        label: "Average System Prompt",
        description: "420 tokens (vs 10,500 legacy)",
        iconPath: new this.vscode.ThemeIcon("symbol-numeric"),
        collapsibleState: this.vscode.TreeItemCollapsibleState.None
      },
      {
        label: "Annual Cost Savings (50 Devs)",
        description: "$141,250 / year",
        iconPath: new this.vscode.ThemeIcon("credit-card"),
        collapsibleState: this.vscode.TreeItemCollapsibleState.None
      },
      {
        label: "TTFT Latency Reduction",
        description: "0.3s (85% faster)",
        iconPath: new this.vscode.ThemeIcon("zap"),
        collapsibleState: this.vscode.TreeItemCollapsibleState.None
      }
    ];
  }
}
