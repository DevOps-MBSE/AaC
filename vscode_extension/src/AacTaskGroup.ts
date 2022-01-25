import { TaskGroup } from "vscode";

export class AacTaskGroup implements TaskGroup {
    isDefault: boolean | undefined = true;
    id: string = "aac";
}
