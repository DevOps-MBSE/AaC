import { ExtensionContext, window, commands, workspace } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { executeAacCommand, getAaCVersion } from "./aacExecutableWrapper";
import { getOutputChannel } from "./outputChannel";
import { setFilePathConfigurationItem } from "./configuration";

let aacLspClient: AacLanguageServerClient = AacLanguageServerClient.getLspClient();

const EXECUTE_AAC_COMMAND_NAME = "aac.execute";
const CHANGE_AAC_PATH_SETTING_NAME = "aac.changeAacPath";

export function activate(context: ExtensionContext) {
    registerCommands(context);
    workspace.onDidChangeConfiguration(_ => activatePlugin(context));
    getAaCVersion().then(installedAaCVersion => {
        if (installedAaCVersion) {
            activatePlugin(context);
        } else {
            const missingAacMessage = "Please install AaC locally to activate these plugin features.\n 'pip install aac'";
            window.showErrorMessage(missingAacMessage);
        }
    });
}

function activatePlugin(context: ExtensionContext) {
    aacLspClient.startLanguageServer(context);
}

function registerCommands(context: ExtensionContext) {
    context.subscriptions.push(commands.registerCommand(EXECUTE_AAC_COMMAND_NAME, executeAacCommand));
    context.subscriptions.push(commands.registerCommand(CHANGE_AAC_PATH_SETTING_NAME, () => setFilePathConfigurationItem("aacPath", "Select the AaC executable")));
}

export function deactivate(): void {
    aacLspClient.shutdownServer();
    getOutputChannel().dispose();
}
