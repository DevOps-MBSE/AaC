import * as vscode from 'vscode';
import { AacTaskProvider } from './AacTaskProvider';

let aacTaskProvider: vscode.Disposable | undefined;

export function activate() {

    aacTaskProvider = vscode.tasks.registerTaskProvider(AacTaskProvider.aacType, new AacTaskProvider());

    console.log('Congratulations, your extension "AaC" is now active!');
}

export function deactivate(): void {
    if (aacTaskProvider) {
        aacTaskProvider.dispose();
    }
}
