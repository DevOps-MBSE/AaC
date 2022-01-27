import * as path from 'path';
import * as fs from 'fs';
import * as cp from 'child_process';
import * as vscode from 'vscode';
import { error } from 'console';
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
		// A Aac task consists of a task and an optional file as specified in AacTaskDefinition
		// Make sure that this looks like a Aac task by checking that there is a task.
		if (task) {
			// resolveTask requires that the same definition object be used.
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

async function execAac(command: string, args: Array<string>): Promise<string> {

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
        console.error(err)
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

    console.log(result)
	return result;
}

async function getAacTasks(): Promise<vscode.Task[]> {

    const commandLine = 'aac -h';

    return execAac("", ["-h"]).then(aacHelpOutput => {
        const result: vscode.Task[] = [];

        const regExp = /{(.*)}/;
        const commandNamesMatch = regExp.exec(aacHelpOutput);

        let commandNames: Array<string> = []
        if (commandNamesMatch && commandNamesMatch.length >= 2) {
            commandNames = commandNamesMatch[1].split(",")
        }

        for (const commandName of commandNames) {

            const commandNameRegexPattern = `\\\s+${commandName}[\\s|\\n]*\\s(.*)`
            var regex = new RegExp(commandNameRegexPattern, "g");
            const matches = regex.exec(aacHelpOutput)
            if (matches && matches.length > 0) {
                var commandDescription = matches[1]

                const taskDefinition: AacTaskDefinition = {
                    type: AacTaskProvider.AacType,
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