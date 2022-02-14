import { Disposable, ExtensionContext, tasks } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { AacTaskProvider } from "./AacTaskProvider";

let aacTaskProvider: Disposable | undefined;
let aacLspClient: AacLanguageServerClient = AacLanguageServerClient.makeLspClient();

export function activate(context: ExtensionContext) {
    aacTaskProvider = tasks.registerTaskProvider(AacTaskProvider.aacType, new AacTaskProvider());
    aacLspClient.startLanguageServer(context);
}

export function deactivate(): void {
    aacTaskProvider?.dispose();
    aacLspClient.shutdownServer();
}
