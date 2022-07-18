import * as vscode from 'vscode';
import * as path from 'path';
import { aacRestApi, DefinitionModel } from "../requests/aacRequests"

export class AacDefinitionsViewProvider implements vscode.TreeDataProvider<Definition> {
    constructor() { }

    getTreeItem(element: Definition): vscode.TreeItem {
        return element;
    }

    getChildren(element?: Definition): Thenable<Definition[]> {
        if (element) {
            return Promise.resolve(
                this.getDefinitionsInContext()
            );
        } else {
            return Promise.resolve(this.getDefinitionsInContext());
        }
    }

    private async getDefinitionsInContext(): Promise<Definition[]> {
        const definitionModels = (await Promise.resolve(aacRestApi.getDefinitionsDefinitionsGet()))
        return definitionModels.map((definitionModel: DefinitionModel) => new Definition(definitionModel, vscode.TreeItemCollapsibleState.None))
    }
}
class Definition extends vscode.TreeItem {
    constructor(
        public readonly definitionModel: DefinitionModel,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(definitionModel.name, collapsibleState);
        this.tooltip = `${definitionModel.name}`;
        this.description = `${definitionModel.name}`;
    }

    iconPath = {
        light: path.join(__filename, '..', '..', 'resources', 'light', 'dependency.svg'),
        dark: path.join(__filename, '..', '..', 'resources', 'dark', 'dependency.svg')
    };
}

function getDefinitionByName(definitionName: string) {
    return Promise.resolve(aacRestApi.getDefinitionByNameDefinitionGet({name: definitionName}))
}

export function onDefinitionNodeSelection(event: vscode.TreeViewSelectionChangeEvent<Definition>) {
    if (event.selection.length > 0) {
        getDefinitionByName(event.selection[0].definitionModel.name).then(response => {
            console.log(response)
            vscode.commands.executeCommand(
                "vscode.openWith",
                vscode.Uri.from({scheme: "untitled", path:`${response.name}`}),
                "aac.visualEditor"
            );
        })
    }
}