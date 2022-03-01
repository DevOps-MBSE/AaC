import { Disposable, ExtensionContext, tasks, commands } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { executeAacCommand } from "./aacExecutableWrapper";
import { getOutputChannel } from "./outputChannel";
import { assertCorrectAacVersionIsInstalled } from "./helpers";

let aacLspClient: AacLanguageServerClient = AacLanguageServerClient.getLspClient();

export function activate(context: ExtensionContext) {

    assertCorrectAacVersionIsInstalled();
    aacLspClient.startLanguageServer(context);
    context.subscriptions.push(
        commands.registerCommand('aac.execute', executeAacCommand)
    );
}

export function deactivate(): void {
    aacLspClient.shutdownServer();
    getOutputChannel().dispose();
}
