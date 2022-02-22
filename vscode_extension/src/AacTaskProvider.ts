import * as vscode from 'vscode';
import { AacTaskGroup } from './AacTaskGroup';
import { execShell } from './helpers';

export class AacTaskProvider implements vscode.TaskProvider {
    static aacType: string = 'aac';
    private aacTaskPromise: vscode.ProviderResult<vscode.Task[]> | undefined = undefined;

    constructor() { }

    public provideTasks(): vscode.ProviderResult<vscode.Task[]> {
        if (!this.aacTaskPromise) {
            this.aacTaskPromise = getAacTasks();
        }
        return this.aacTaskPromise;
    }

    public resolveTask(_task: vscode.Task): vscode.ProviderResult<vscode.Task> {
        const task = _task.definition.task;
        if (task) {
            const definition: AacTaskDefinition = <any>_task.definition;
            return new vscode.Task(definition, _task.scope ?? vscode.TaskScope.Workspace, definition.task, 'aac', new vscode.ShellExecution(`aac ${definition.task}`));
        }
        return undefined;
    }
}

let _channel: vscode.OutputChannel;
function getOutputChannel(): vscode.OutputChannel {
    // Creates a new entry in the "OUTPUT" panel at the bottom of the IDE.
    if (!_channel) {
        _channel = vscode.window.createOutputChannel('Architecture-as-Code');
    }
    return _channel;
}

interface AacTaskDefinition extends vscode.TaskDefinition {
    /**
     * The task name
     */
    name: string;
}

async function execAacShellCommand(command: string, args: Array<string> = []): Promise<string> {

    let result: string = "";

    const outputChannel = getOutputChannel();

    let commandArgsArray = ["aac", command, ...args];
    try {
        const { stdout, stderr } = await execShell(commandArgsArray.join(" "), {});
        if (stderr && stderr.length > 0) {
            outputChannel.appendLine(stderr);
            outputChannel.show(true);
        }
        if (stdout) {
            result = stdout;
        }
    } catch (error: any) {
        let errorMessage = error.stderr || error.stdout || "";

        outputChannel.appendLine(`Failed to execute AaC command:\n${errorMessage}`);
        outputChannel.show(true);
        throw error;
    }

    return result;
}

async function getAacTasks(): Promise<vscode.Task[]> {

    return execAacShellCommand("-h").then(aacHelpOutput => {
        const result: vscode.Task[] = [];

        const regExp = /{(.*)}/;
        const commandNamesMatch = regExp.exec(aacHelpOutput);

        let commandNames: Array<string> = [];
        if (commandNamesMatch && commandNamesMatch.length >= 2) {
            commandNames = commandNamesMatch[1].split(",");
        }

        for (const commandName of commandNames) {

            const commandNameRegexPattern = `\\\s+${commandName}[\\s|\\n]*\\s(.*)`;
            const regex = new RegExp(commandNameRegexPattern, "g");
            const matches = regex.exec(aacHelpOutput);
            if (matches && matches.length > 0) {
                // We can extract the command description with the following use of group matches
                // const commandDescription = matches[1]

                const taskDefinition: AacTaskDefinition = {
                    type: "shell",
                    name: commandName
                };

                const task = new vscode.Task(taskDefinition, vscode.TaskScope.Workspace, commandName, 'aac', new vscode.ShellExecution(`aac ${commandName}`));
                task.group = new AacTaskGroup();
                result.push(task);
            }
        }

        return result;
    });
}