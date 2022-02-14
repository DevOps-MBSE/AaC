import { workspace } from "vscode";

export function ensure(messageIfTestFails: string, test: (...args: any[]) => boolean, ...args: any[]): void {
    if (!test(...args)) {
        throw new Error(messageIfTestFails);
    }
}

export function ensureTrue(messageIfTestFails: string, test: boolean): void {
    ensure(messageIfTestFails, () => test);
}

export function getConfigurationItem(name: string): any {
    return workspace.getConfiguration().get(`aac.${name}`) ?? null;
}
