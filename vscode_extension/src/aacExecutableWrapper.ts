import { execShell } from "./helpers";
import { getOutputChannel } from "./outputChannel"
import { window, QuickPickOptions, InputBoxOptions, OpenDialogOptions, Uri } from 'vscode';

const outputChannel = getOutputChannel();

interface CommandArgument {
    name: string;
    description: string;
    userResponse?: string;
}

/**
 * Prompts the user for input then executes the AaC plugin with user-provided
 *  information and arguments.
 */
 export async function executeAacCommand(): Promise<void> {

    let availableCommands: string[] = await getAacCommandNames();

    const quickPickOptions: QuickPickOptions = {
        canPickMany: false,
    }

    window.showQuickPick(availableCommands, quickPickOptions).then(commandName => {
        if(commandName) {
            getAacCommandArgs(commandName).then(async (commandArguments) => {
                await getCommandArgUserInput(commandArguments);
                execAacShellCommand(commandName, commandArguments).then(output => {
                    outputChannel.appendLine(output)
                    outputChannel.show()
                })
            });
        }
    })
}

async function getCommandArgUserInput(commandArguments: CommandArgument[]) {

    let unansweredCommandArguments: CommandArgument[] = commandArguments.filter(argument => { return (argument.userResponse === undefined) } );

    if (unansweredCommandArguments.length > 0) {
        let argumentToPromptFor = unansweredCommandArguments[0]
        const dialogBoxOptions: OpenDialogOptions = {
            title: argumentToPromptFor.name,
        }
        const inputBoxOptions: InputBoxOptions = {
            title: argumentToPromptFor.name,
            prompt: argumentToPromptFor.description,
        }

        if (argumentToPromptFor.description.toLowerCase().includes("path")){
            let fileUri: Uri[] | undefined = await window.showOpenDialog(inputBoxOptions)
            if(fileUri)
                argumentToPromptFor.userResponse = fileUri[0]?.path
        } else {
            argumentToPromptFor.userResponse = await window.showInputBox(inputBoxOptions)
        }
    } else if(unansweredCommandArguments.length > 1) {
        getCommandArgUserInput(commandArguments)
    }
}

async function getAacCommandNames(): Promise<string[]> {
    const aacHelpOutput = await execAacShellCommand("-h");
    return parseTaskNamesFromHelpCommand(aacHelpOutput);
}

/**
 * @returns Promise<CommandArgument[]> Command arguments
 */
async function getAacCommandArgs(aacCommandName: string): Promise<CommandArgument[]> {
    const aacHelpOutput = await execAacShellCommand(`${aacCommandName} -h`);
    return parseTaskArgsFromHelpCommand(aacHelpOutput);
}

async function execAacShellCommand(command: string, commandArgs: CommandArgument[] = []): Promise<string> {

    let result: string = "";

    let commandArgsArray = ["aac", command, ...(commandArgs.map(argument => argument.userResponse))];
    try {
        const { stdout, stderr } = await execShell(commandArgsArray.join(" "), {});
        const stringOutput = stderr.length > 0 ? stderr : stdout
        return stringOutput;

    } catch (error: any) {
        let errorMessage = error.stderr || error.stdout || "";

        outputChannel.appendLine(`Failed to execute AaC command:\n${errorMessage}`);
        outputChannel.show(true);
        throw error;
    }
}

function parseTaskNamesFromHelpCommand(aacHelpOutput: string): string[] {

    const regExp = /{(.*)}/;
    const commandNamesMatch = regExp.exec(aacHelpOutput);

    let commandNames: string[] = [];
    if (commandNamesMatch && commandNamesMatch.length >= 2) {
        commandNames = commandNamesMatch[1].split(",");
    }

    return commandNames;
}

function parseTaskArgsFromHelpCommand(aacHelpOutput: string): CommandArgument[] {

    const regExp = /^  (?<argName>\S+)*\s*(?<argDescription>.*)$/gm;
    const commandArgumentsMatch = regExp.exec(aacHelpOutput);

    let commandArguments: CommandArgument[] = [];
    if (commandArgumentsMatch) {
        commandArguments.push({
            name: commandArgumentsMatch.groups?.argName || "<argument name>",
            description: commandArgumentsMatch.groups?.argDescription || "<argument description>"
        })
    }

    return commandArguments;
}
