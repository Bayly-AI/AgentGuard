import { QuadGraphWebviewPanel } from "./graphWebview.js";

export function registerCommands(vscode: any, context: any, client: any, providers: { planes: any; gates: any; finops: any }) {
  const outputChannel = vscode.window.createOutputChannel("AgentGuard");

  context.subscriptions.push(
    vscode.commands.registerCommand("agentguard.sync", async () => {
      try {
        vscode.window.showInformationMessage("AgentGuard: Synchronizing workspace substrate...");
        const res = await client.sync();
        outputChannel.appendLine(`[Sync]\n${res}`);
        providers.planes.refresh();
        providers.gates.refresh();
        providers.finops.refresh();
        vscode.window.showInformationMessage("✓ AgentGuard: Substrate successfully synchronized.");
      } catch (err: any) {
        vscode.window.showErrorMessage(`AgentGuard Sync Error: ${err.message}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("agentguard.validate", async () => {
      try {
        vscode.window.showInformationMessage("AgentGuard: Auditing Quad-Graph topology...");
        const report = await client.validate();
        if (report.is_valid) {
          vscode.window.showInformationMessage(`✓ Quad-Graph Valid: 0 cycles detected.`);
        } else {
          vscode.window.showWarningMessage(`⚠ Quad-Graph Warning: ${report.cycle_count} cycles found.`);
        }
      } catch (err: any) {
        vscode.window.showErrorMessage(`AgentGuard Validation Error: ${err.message}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("agentguard.qualityGate", async () => {
      try {
        vscode.window.showInformationMessage("AgentGuard: Running Hath0r Quality Gates...");
        const res = await client.runQualityGate();
        outputChannel.appendLine(`[Quality Gate]\n${res}`);
        outputChannel.show();
        vscode.window.showInformationMessage("✓ Hath0r Quality Gates Passed.");
      } catch (err: any) {
        vscode.window.showErrorMessage(`Quality Gate Error: ${err.message}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("agentguard.prompt", async () => {
      const role = await vscode.window.showQuickPick(["architect", "developer", "reviewer"], {
        placeHolder: "Select role for zero-prompt-tax system prompt synthesis"
      });
      if (role) {
        const prompt = await client.synthesizePrompt(role);
        outputChannel.appendLine(`[System Prompt for ${role}]\n${prompt}`);
        outputChannel.show();
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("agentguard.finops", async () => {
      const finops = await client.getFinOps();
      vscode.window.showInformationMessage(
        `💰 AgentGuard FinOps: ${finops.prompt_tokens_saved_pct}% Token Reduction | Avg Prompt: ${finops.average_prompt_tokens} tokens | Net Savings: ${finops.annual_savings_estimate}/yr`
      );
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("agentguard.visualize", () => {
      QuadGraphWebviewPanel.createOrShow(vscode, client);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("agentguard.refresh", () => {
      providers.planes.refresh();
      providers.gates.refresh();
      providers.finops.refresh();
    })
  );
}
