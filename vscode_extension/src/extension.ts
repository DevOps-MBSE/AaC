import { Disposable, ExtensionContext, tasks, commands, window } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { AacTaskProvider } from "./AacTaskProvider";
import { executeAacCommand } from "./aacExecutableWrapper";
import { getOutputChannel } from "./outputChannel";

let aacTaskProvider: Disposable | undefined;
let aacLspClient: AacLanguageServerClient = AacLanguageServerClient.getLspClient();

export function activate(context: ExtensionContext) {
    aacTaskProvider = tasks.registerTaskProvider(AacTaskProvider.aacType, new AacTaskProvider());
    aacLspClient.startLanguageServer(context);
    context.subscriptions.push(
        commands.registerCommand('aac.execute', executeAacCommand)
    );
}

export function deactivate(): void {
    aacTaskProvider?.dispose();
    aacLspClient.shutdownServer();
    getOutputChannel().dispose();
}
