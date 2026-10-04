import { ExtensionAgentGuardClient } from "./client.js";
import { PlanesTreeProvider } from "./treeViews/planesTreeProvider.js";
import { GatesTreeProvider } from "./treeViews/gatesTreeProvider.js";
import { FinOpsTreeProvider } from "./treeViews/finopsTreeProvider.js";
import { registerCommands } from "./commands.js";

export function activate(context: any) {
  let vscode: any;
  try {
    vscode = require("vscode");
  } catch {
    // Non-VSCode runtime fallback
    return;
  }

  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();
  const config = vscode.workspace.getConfiguration("agentguard");
  const execPath = config.get("executablePath", "");

  const client = new ExtensionAgentGuardClient(workspaceRoot, execPath);

  const planesProvider = new PlanesTreeProvider(client, vscode);
  const gatesProvider = new GatesTreeProvider(client, vscode);
  const finopsProvider = new FinOpsTreeProvider(client, vscode);

  vscode.window.registerTreeDataProvider("agentguard-planes", planesProvider);
  vscode.window.registerTreeDataProvider("agentguard-gates", gatesProvider);
  vscode.window.registerTreeDataProvider("agentguard-finops", finopsProvider);

  registerCommands(vscode, context, client, {
    planes: planesProvider,
    gates: gatesProvider,
    finops: finopsProvider
  });

  if (config.get("autoSyncOnSave", true)) {
    context.subscriptions.push(
      vscode.workspace.onDidSaveTextDocument(async (doc: any) => {
        if (
          doc.fileName.endsWith("AGENTS.md") ||
          doc.fileName.endsWith(".agentguard") ||
          doc.fileName.endsWith("rules.md")
        ) {
          try {
            await client.sync();
            planesProvider.refresh();
          } catch {
            // Ignore background sync errors
          }
        }
      })
    );
  }
}

export function deactivate() {}
