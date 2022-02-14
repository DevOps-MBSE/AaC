import { Disposable, ExtensionContext, tasks } from "vscode";
import { AacLanguageServerClient } from "./AacLanguageServer";
import { AacTaskProvider } from "./AacTaskProvider";

let aacTaskProvider: Disposable | undefined;

export function activate(context: ExtensionContext) {
    aacTaskProvider = tasks.registerTaskProvider(AacTaskProvider.aacType, new AacTaskProvider());
    AacLanguageServerClient.makeLspClient().startLanguageServer(context);
}

export function deactivate(): void {
    aacTaskProvider?.dispose();
    AacLanguageServerClient.makeLspClient().shutdownServer();
}
