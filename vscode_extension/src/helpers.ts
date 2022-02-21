import { workspace } from "vscode";

export function ensure(test: () => boolean, failureMessage: string): void {
    if (!test()) {
        throw new Error(failureMessage);
    }
}

export function ensureTrue(test: boolean, failureMessage: string): void {
    ensure(() => test, failureMessage);
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
