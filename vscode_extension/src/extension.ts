import { ExtensionContext, commands, workspace, window } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { executeAacCommand } from "./aacExecutableWrapper";
import { getOutputChannel } from "./outputChannel";
import { AacDefinitionEditorProvider } from "./providers/AacDefinitionEditorProvider";
import { AacDefinitionsViewProvider, Definition, editDefinition, deleteDefinition, onDefinitionNodeSelection } from "./providers/AacDefinitionsViewProvider";
import { setFilePathConfigurationItem } from "./configuration";

let aacLspClient: AacLanguageServerClient = AacLanguageServerClient.getLspClient();

const EXECUTE_AAC_COMMAND_NAME = "aac.execute";
const CHANGE_AAC_PATH_SETTING_NAME = "aac.changeAacPath";
const TREE_VIEW_PROVIDER = new AacDefinitionsViewProvider();

export function activate(context: ExtensionContext) {
    registerCommands(context);
    activatePlugin(context);
    workspace.onDidChangeConfiguration(_ => activatePlugin(context));
}

function activatePlugin(context: ExtensionContext) {
    aacLspClient.startLanguageServer(context);
    context.subscriptions.push(AacDefinitionEditorProvider.register(context));

    window.createTreeView('definitions-in-context', { treeDataProvider: TREE_VIEW_PROVIDER });
    const definitionsView = window.createTreeView('definitions-in-context', { treeDataProvider: TREE_VIEW_PROVIDER});
    definitionsView.onDidChangeSelection(e => {
        onDefinitionNodeSelection(e)
    })
}

function registerCommands(context: ExtensionContext) {
    const commandsToRegister = [
        [EXECUTE_AAC_COMMAND_NAME, executeAacCommand],
        [CHANGE_AAC_PATH_SETTING_NAME, () => setFilePathConfigurationItem("aacPath", "Select the AaC executable")],
        [TREE_VIEW_PROVIDER.COMMAND_DEFINITIONS_LIST_REFRESH, () => { TREE_VIEW_PROVIDER.refresh(); }],
        [TREE_VIEW_PROVIDER.COMMAND_DEFINITIONS_LIST_EDIT, (e: Definition) => { editDefinition(e); }],
        [TREE_VIEW_PROVIDER.COMMAND_DEFINITIONS_LIST_DELETE, (e: Definition) => { deleteDefinition(e, TREE_VIEW_PROVIDER); }],
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
