import { window } from "vscode";

export function assert(test: () => boolean, failureMessage: string): void {
    if (!test()) {
        window.showErrorMessage(failureMessage);
    }
}

export function assertTrue(test: boolean, failureMessage: string): void {
    assert(() => test, failureMessage);
}

export function showMessageOnError(action: () => any, failureMessage: string): any {
    try {
        return action();
    } catch (onFailure) {
        window.showErrorMessage(`${failureMessage}\n${onFailure}`);
    }
}
