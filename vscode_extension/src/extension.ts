import { ExtensionContext, window, commands } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { executeAacCommand, getAaCVersion } from "./aacExecutableWrapper";
import { getOutputChannel } from "./outputChannel";

let aacLspClient: AacLanguageServerClient = AacLanguageServerClient.getLspClient();

const EXECUTE_AAC_COMMAND_NAME = "aac.execute";

export function activate(context: ExtensionContext) {

    getAaCVersion().then(installedAaCVersion => {
        if (installedAaCVersion) {
            aacLspClient.startLanguageServer(context);
            context.subscriptions.push(
                commands.registerCommand(EXECUTE_AAC_COMMAND_NAME, executeAacCommand)
            );
        } else {
            const missingAacMessage = `Please install AaC locally to activate
                these plugin features.\n 'pip install aac'`;

            commands.registerCommand(EXECUTE_AAC_COMMAND_NAME, () => {
                window.showErrorMessage(missingAacMessage);
            });
            window.showErrorMessage(missingAacMessage);
        }
    });
}

export function deactivate(): void {
    aacLspClient.shutdownServer();
    getOutputChannel().dispose();
}
