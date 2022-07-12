import { ExtensionContext, window, commands } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { executeAacCommand, getAaCVersion } from "./aacExecutableWrapper";
import { getOutputChannel } from "./outputChannel";
import { AacDefinitionsViewProvider } from "./providers/AacDefinitionsViewProvider"

let aacLspClient: AacLanguageServerClient = AacLanguageServerClient.getLspClient();

const EXECUTE_AAC_COMMAND_NAME = "aac.execute";

export function activate(context: ExtensionContext) {

    getAaCVersion().then(installedAaCVersion => {
        if (installedAaCVersion) {
            activatePlugin(context);
        } else {
            const missingAacMessage = "Please install AaC locally to activate these plugin features.\n 'pip install aac'";

            commands.registerCommand(EXECUTE_AAC_COMMAND_NAME, () => window.showErrorMessage(missingAacMessage));
            window.showErrorMessage(missingAacMessage);
        }
    });
}

function activatePlugin(context: ExtensionContext) {
    aacLspClient.startLanguageServer(context);
    context.subscriptions.push(
        commands.registerCommand(EXECUTE_AAC_COMMAND_NAME, executeAacCommand)
    );

    const aacDefinitionsViewProvider = new AacDefinitionsViewProvider();
	window.registerTreeDataProvider('definitions-in-context', aacDefinitionsViewProvider);
}

export function deactivate(): void {
    aacLspClient.shutdownServer();
    getOutputChannel().dispose();
}
