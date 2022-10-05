import { window, workspace } from "vscode";

export function getConfigurationItem(name: string): any {
    return workspace.getConfiguration().get(`aac.${name}`) ?? null;
}

export async function setFilePathConfigurationItem(name: string, title: string) {
    const dialogOptions = { title: title, canSelectMany: false };
    await window.showOpenDialog(dialogOptions).then(values => {
        if (values) {
            workspace.getConfiguration("aac").update(name, values[0].fsPath);
        }
    });
}
