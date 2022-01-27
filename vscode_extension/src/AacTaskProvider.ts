import * as path from 'path';
import * as fs from 'fs';
import * as cp from 'child_process';
import * as vscode from 'vscode';
import { AacTaskGroup } from './AacTaskGroup';

export class AacTaskProvider implements vscode.TaskProvider {
	static AacType = 'aac';
	private aacTaskPromise: vscode.ProviderResult<vscode.Task[]> | undefined = undefined;

	constructor() {}

	public provideTasks(token: vscode.CancellationToken): vscode.ProviderResult<vscode.Task[]> {
		if (!this.aacTaskPromise) {
            console.log("Loading extension tasks");
			this.aacTaskPromise = getAacTasks();
		}
		return this.aacTaskPromise;
	}

	public resolveTask(_task: vscode.Task, token: vscode.CancellationToken): vscode.ProviderResult<vscode.Task> {
		const task = _task.definition.task;
		if (task) {
			const definition: AacTaskDefinition = <any>_task.definition;
			return new vscode.Task(definition, _task.scope ?? vscode.TaskScope.Workspace, definition.task, 'aac', new vscode.ShellExecution(`aac ${definition.task}`));
		}
		return undefined;
	}
}

function exec(command: string, options: cp.ExecOptions): Promise<{ stdout: string; stderr: string }> {
	return new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
		cp.exec(command, options, (error, stdout, stderr) => {
			if (error) {
				reject({ error, stdout, stderr });
			}
			resolve({ stdout, stderr });
		});
	});
}

let _channel: vscode.OutputChannel;
function getOutputChannel(): vscode.OutputChannel {
	if (!_channel) {
		_channel = vscode.window.createOutputChannel('Aac Auto Detection');
	}
	return _channel;
}

interface AacTaskDefinition extends vscode.TaskDefinition {
	/**
	 * The task name
	 */
	task: string;
}

async function execAacShellCommand(command: string, args: Array<string> = []): Promise<string> {

    let result: string = "";

    let commandArgsArray = ["aac", command, ...args]
    try {
        const { stdout, stderr } = await exec(commandArgsArray.join(" "), {});
        if (stderr && stderr.length > 0) {
            getOutputChannel().appendLine(stderr);
            getOutputChannel().show(true);
        }
        if (stdout) {
            result = stdout
        }
    } catch (err: any) {
        const channel = getOutputChannel();
        if (err.stderr) {
            channel.appendLine(err.stderr);
        }
        if (err.stdout) {
            channel.appendLine(err.stdout);
        }
        channel.appendLine('Failed to execute AaC command');
        channel.show(true);
        throw err
    }

	return result;
}

async function getAacTasks(): Promise<vscode.Task[]> {

    return execAacShellCommand("-h").then(aacHelpOutput => {
        const result: vscode.Task[] = [];

        const regExp = /{(.*)}/;
        const commandNamesMatch = regExp.exec(aacHelpOutput);

        let commandNames: Array<string> = []
        if (commandNamesMatch && commandNamesMatch.length >= 2) {
            commandNames = commandNamesMatch[1].split(",")
        }

        for (const commandName of commandNames) {

            const commandNameRegexPattern = `\\\s+${commandName}[\\s|\\n]*\\s(.*)`
            const regex = new RegExp(commandNameRegexPattern, "g");
            const matches = regex.exec(aacHelpOutput)
            if (matches && matches.length > 0) {
                // We can extract the command description with the following use of group matches
                // const commandDescription = matches[1]

                const taskDefinition: AacTaskDefinition = {
                    type: "shell",
                    task: commandName
                };

                const task = new vscode.Task(taskDefinition, vscode.TaskScope.Workspace, commandName, 'aac', new vscode.ShellExecution(`aac ${commandName}`));
                task.group = new AacTaskGroup();
                result.push(task);
            }
        }

        return result;
    })
}