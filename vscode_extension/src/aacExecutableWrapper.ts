import { execShell } from "./shell";
import { getConfigurationItem } from "./configuration";
import { getOutputChannel } from "./outputChannel";
import { window, QuickPickOptions, InputBoxOptions, OpenDialogOptions, Uri } from 'vscode';

const outputChannel = getOutputChannel();

interface CommandArgument {
    name: string;
    description: string;
    dataType?: string;
    userResponse?: string;
    optional?: boolean;
}

interface Command {
    name: string;
    description: string;
    arguments: CommandArgument[];
}

/**
 * Prompts the user for input then executes the AaC plugin with user-provided
 * information and arguments.
 */
export async function executeAacCommand(): Promise<void> {
    const helpDumpOutput = await execAacShellCommand("help-dump");
    const helpJson: string = helpDumpOutput.split("\n").filter(it => it !== "")[1];
    const availableCommands: Command[] = JSON.parse(helpJson);

    const quickPickOptions: QuickPickOptions = {
        canPickMany: false,
    };

    window.showQuickPick(availableCommands.map(it => it.name), quickPickOptions)
        .then(commandName => {
            executeCommandWithArguments(availableCommands.filter(it => it.name === commandName)[0])
                .then((output: string) => {
                    outputChannel.appendLine(output);
                    outputChannel.show();
                });
        });
}

export async function executeCommandWithArguments(command: Command): Promise<string> {
    await getCommandArgUserInput(command.arguments);
    return await execAacShellCommand(command.name, command.arguments);
}

/**
 * Gets the version of the currently installed AaC package
 * @returns string of the version number or null if not installed.
 */
export async function getAaCVersion(): Promise<string | null> {
    let aacVersionOutput: string = "";
    try {
        aacVersionOutput = await execAacShellCommand("version");
    } catch (exception) {
        // TODO: Change to logging or alternative
    }

    const regExp = /([0-9]+\.*){3}/;
    const versionMatch = regExp.exec(aacVersionOutput);
    return versionMatch ? versionMatch[0] : null;
}

async function getCommandArgUserInput(commandArguments: CommandArgument[]) {
    const hasPathArgument = (argument: CommandArgument, options: string[]) =>
        options.some(option => argument.description?.toLowerCase().includes(option));

    let argumentsWithoutUserResponse: CommandArgument[] = commandArguments
        .filter(argument => !argument.userResponse)
        .filter(argument => !argument.name?.includes("--help"));

    for (let index = 0; index < argumentsWithoutUserResponse.length; ++index) {
        let argumentToPromptUserFor = argumentsWithoutUserResponse[index];
        if (hasPathArgument(argumentToPromptUserFor, ["path", "file", "directory"])) {
            const dialogBoxOptions: OpenDialogOptions = {
                title: argumentToPromptUserFor.name,
                canSelectMany: hasPathArgument(argumentToPromptUserFor, ["paths", "files", "directories"]),
                canSelectFolders: hasPathArgument(argumentToPromptUserFor, ["directory", "directories"]),
            };

            let fileUris: Uri[] | undefined = await window.showOpenDialog(dialogBoxOptions);
            argumentToPromptUserFor.userResponse = fileUris ? fileUris.map(uri => uri.path).join(",") : "";
        } else {
            let placeholderText = "Optional Argument. Escape to Skip"

            argumentToPromptUserFor.optional ? placeholderText = placeholderText : placeholderText = ""

            const inputBoxOptions: InputBoxOptions = {
                title: argumentToPromptUserFor.name,
                placeHolder: placeholderText,
                prompt: argumentToPromptUserFor.description,
            };

            argumentToPromptUserFor.userResponse = await window.showInputBox(inputBoxOptions);
        }
    }
}

/**
 * Executes AaC commands with arguments.
 * @param command - AaC command name
 * @param commandArgs - command arguments and
 * @returns
 */
async function execAacShellCommand(command: string, commandArgs: CommandArgument[] = []): Promise<string> {
    const commandArgsArray = commandArgs
        .filter(argument => argument.userResponse)
        .map(argument => argument.optional ? `${argument.name} ${argument.userResponse}` : argument.userResponse);

    const aac = getConfigurationItem("aacPath");
    try {
        const { stdout, stderr } = await execShell([aac, command, ...commandArgsArray].join(" "), {});
        return stderr.length > 0 ? stderr : stdout;
    } catch (error: any) {
        let errorMessage = error.stderr || error.stdout || "unrecognized error";

        outputChannel.appendLine(`Failed to execute AaC command:\n${errorMessage}`);
        outputChannel.show(true);
        throw error;
    }
}
