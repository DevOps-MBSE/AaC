import * as vscode from 'vscode';
import { aacRestApi, DefinitionModel } from "../requests/aacRequests";

export class AacDefinitionsViewProvider implements vscode.TreeDataProvider<Definition> {

    public COMMAND_DEFINITIONS_LIST_REFRESH = "definitionsList.refreshEntry";
    public COMMAND_DEFINITIONS_LIST_EDIT = "definitionsList.editEntry";
    public COMMAND_DEFINITIONS_LIST_DELETE = "definitionsList.deleteEntry";
    private _onDidChangeTreeData: vscode.EventEmitter<Definition | undefined | void> = new vscode.EventEmitter<Definition | undefined | void>();
    readonly onDidChangeTreeData: vscode.Event<Definition | undefined | void> = this._onDidChangeTreeData.event;

    constructor() { }

    public getTreeItem(element: Definition): vscode.TreeItem {
        return element;
    }

    public getChildren(element?: Definition): Thenable<Definition[]> {
        if (element) {
            return Promise.resolve(
                this.getDefinitionsInContext()
            );
        } else {
            return Promise.resolve(this.getDefinitionsInContext());
        }
    }

    public refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    private async getDefinitionsInContext(): Promise<Definition[]> {
        const requestResponse = (await Promise.resolve(aacRestApi.getDefinitionsDefinitionsGet()));
        return requestResponse.body.map((definition: DefinitionModel) => new Definition(definition, vscode.TreeItemCollapsibleState.None));
    }
}

export class Definition extends vscode.TreeItem {
    constructor(
        public readonly definitionModel: DefinitionModel,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {

        super(definitionModel.name, collapsibleState);
        this.definitionType = Object.keys(definitionModel.structure)[0];
        this.description = `${this.definitionType}`;
        this.tooltip = `Open the ${this.definitionType} definition "${definitionModel.name}" in a visual editor.\nThe definition originates from ${definitionModel.sourceUri}`;
        this.iconPath = {
            light: "",
            dark:  ""
        };
    }

    private definitionType: string;
}

function getDefinitionByName(definitionName: string) {
    return Promise.resolve(aacRestApi.getDefinitionByNameDefinitionGet(definitionName, true));
}

function deleteDefinitionByName(definitionName: string) {
    return Promise.resolve(aacRestApi.removeDefinitionByNameDefinitionDelete(definitionName));
}

export function editDefinition(event: Definition) {
    if (Object.keys(event.definitionModel).length > 0) {
        getDefinitionByName(event.definitionModel.name).then(response => {
            vscode.commands.executeCommand(
                "vscode.openWith",
                vscode.Uri.from({scheme: "untitled", path:`${response.body.name}`}),
                "aac.visualEditor"
            );
        });
    }
}

export function deleteDefinition(event: Definition, viewProvider: AacDefinitionsViewProvider) {
    if (Object.keys(event.definitionModel).length > 0) {
        deleteDefinitionByName(event.definitionModel.name).then(() => {
            viewProvider.refresh();
        });
    }
}

export function onDefinitionNodeSelection(event: vscode.TreeViewSelectionChangeEvent<Definition>) {
    if (event.selection.length > 0) {
        getDefinitionByName(event.selection[0].definitionModel.name).then(response => {
            vscode.commands.executeCommand(
                "vscode.openWith",
                vscode.Uri.from({scheme: "untitled", path:`${response.body.name}`}),
                "aac.visualEditor"
            );
        });
    }
}