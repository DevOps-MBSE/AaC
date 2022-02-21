import { workspace } from "vscode";

export function ensure(test: () => boolean, messageIfTestFails: string): void {
    if (!test()) {
        throw new Error(messageIfTestFails);
    }
}

export function ensureTrue(test: boolean, messageIfTestFails: string): void {
    ensure(() => test, messageIfTestFails);
}

export function showMessageOnError(action: () => any, failureMessage: string): any {
    try {
        return action();
    } catch (onFailure) {
        throw new Error(`${failureMessage}\n${onFailure}`);
    }
}

export function getConfigurationItem(name: string): any {
    return workspace.getConfiguration().get(`aac.${name}`) ?? null;
}
