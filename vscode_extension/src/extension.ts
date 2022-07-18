import { ExtensionContext, window, commands } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { executeAacCommand, getAaCVersion } from "./aacExecutableWrapper";
import { getOutputChannel } from "./outputChannel";
import { AacDefinitionEditorProvider } from "./providers/AacDefinitionEditorProvider"
import { AacDefinitionsViewProvider, onDefinitionNodeSelection } from "./providers/AacDefinitionsViewProvider"

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

    context.subscriptions.push(AacDefinitionEditorProvider.register(context));

	const definitionsView = window.createTreeView('definitions-in-context', { treeDataProvider: new AacDefinitionsViewProvider() });
    definitionsView.onDidChangeSelection(e => {
        onDefinitionNodeSelection(e)
    })
}

export function deactivate(): void {
    aacLspClient.shutdownServer();
    getOutputChannel().dispose();
}
