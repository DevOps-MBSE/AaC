import * as vscode from 'vscode';
import { AacTaskProvider } from './AacTaskProvider';

let aacTaskProvider: vscode.Disposable | undefined;

export function activate() {

    aacTaskProvider = vscode.tasks.registerTaskProvider(AacTaskProvider.aacType, new AacTaskProvider());

}

export function deactivate(): void {
    if (aacTaskProvider) {
        aacTaskProvider.dispose();
    }
}
