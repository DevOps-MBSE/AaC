import { ExtensionContext, commands, workspace, window } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { executeAacCommand } from "./aacExecutableWrapper";
import { getOutputChannel } from "./outputChannel";
import { AacDefinitionEditorProvider } from "./providers/AacDefinitionEditorProvider";
import { AacDefinitionsViewProvider, onDefinitionNodeSelection } from "./providers/AacDefinitionsViewProvider";
import { setFilePathConfigurationItem } from "./configuration";

let aacLspClient: AacLanguageServerClient = AacLanguageServerClient.getLspClient();

const EXECUTE_AAC_COMMAND_NAME = "aac.execute";
const CHANGE_AAC_PATH_SETTING_NAME = "aac.changeAacPath";

export function activate(context: ExtensionContext) {
    registerCommands(context);
    activatePlugin(context);
    workspace.onDidChangeConfiguration(_ => activatePlugin(context));
}

function activatePlugin(context: ExtensionContext) {
    aacLspClient.startLanguageServer(context);
    context.subscriptions.push(
        commands.registerCommand(EXECUTE_AAC_COMMAND_NAME, executeAacCommand)
    );

    context.subscriptions.push(AacDefinitionEditorProvider.register(context));

    const definitionsView = window.createTreeView('definitions-in-context', {treeDataProvider: new AacDefinitionsViewProvider()});
    definitionsView.onDidChangeSelection((event) => {
        onDefinitionNodeSelection(event);
    });
}

function registerCommands(context: ExtensionContext) {
    const commandsToRegister = [
        [EXECUTE_AAC_COMMAND_NAME, executeAacCommand],
        [CHANGE_AAC_PATH_SETTING_NAME, () => setFilePathConfigurationItem("aacPath", "Select the AaC executable")],
    ];

    commandsToRegister.map(pair => {
        const [name, command] = pair;
        context.subscriptions.push(commands.registerCommand(<string>(name), <(...args: any[]) => any>(command)));
    });
}

export function deactivate(): void {
    aacLspClient.shutdownServer();
    getOutputChannel().dispose();
}
