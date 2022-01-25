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

async function getAacTasks(): Promise<vscode.Task[]> {
	const result: vscode.Task[] = [];

    const commandLine = 'aac -h';

    try {
        const { stdout, stderr } = await exec(commandLine, {});
        if (stderr && stderr.length > 0) {
            getOutputChannel().appendLine(stderr);
            getOutputChannel().show(true);
        }
        if (stdout) {
            console.log(stdout)

            const regExp = /{(.*)}/;
            const commandNamesMatch = regExp.exec(stdout);

            let commandNames: Array<string> = []
            if (commandNamesMatch && commandNamesMatch.length >= 2) {
                commandNames = commandNamesMatch[1].split(",")
            }

            for (const commandName of commandNames) {

                const commandNameRegexPattern = `\\\s+${commandName}[\\s|\\n]*\\s(.*)`
                var regex = new RegExp(commandNameRegexPattern, "g");
                const matches = regex.exec(stdout)
                if (matches && matches.length > 0) {
                    var commandDescription = matches[1]

                    const taskDefinition: AacTaskDefinition = {
                        type: AacTaskProvider.AacType,
                        task: commandName
                    };

                    const task = new vscode.Task(taskDefinition, vscode.TaskScope.Workspace, commandName, 'aac', new vscode.ShellExecution(`aac ${commandName}`));
                    task.group = new AacTaskGroup();
                    result.push(task);
                    // commands[commandName] = commandDescription
                }

                // if (matches && matches.length === 2) {
                //     const taskName = matches[1].trim();
                //     const kind: AacTaskDefinition = {
                //         type: 'aac',
                //         task: taskName
                //     };
                //     const task = new vscode.Task(kind, vscode.TaskScope.Workspace, taskName, 'aac', new vscode.ShellExecution(`aac ${taskName}`));
                //
                //     const lowerCaseLine = line.toLowerCase();
                //     if (isBuildTask(lowerCaseLine)) {
                //         task.group = vscode.TaskGroup.Build;
                //     } else if (isTestTask(lowerCaseLine)) {
                //         task.group = vscode.TaskGroup.Test;
                //     }
                // }
            }
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
        channel.appendLine('Auto detecting aac tasks failed.');
        channel.show(true);
    }

    console.log(result)
	return result;
}