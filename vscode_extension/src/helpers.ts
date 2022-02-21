import { workspace } from "vscode";

export function ensure(messageIfTestFails: string, test: (...args: any[]) => boolean, ...args: any[]): void {
    if (!test(...args)) {
        throw new Error(messageIfTestFails);
    }
}

export function ensureTrue(test: boolean, messageIfTestFails: string): void {
    ensure(messageIfTestFails, () => test);

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
