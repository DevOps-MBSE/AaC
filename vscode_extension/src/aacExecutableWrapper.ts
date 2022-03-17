import { execShell } from "./helpers";
import { getOutputChannel } from "./outputChannel";
import { window, QuickPickOptions, InputBoxOptions, OpenDialogOptions, Uri } from 'vscode';

const outputChannel = getOutputChannel();

interface CommandArgument {
    name?: string;
    description?: string;
    userResponse?: string;
    optional?: boolean;
}

/**
 * Prompts the user for input then executes the AaC plugin with user-provided
 * information and arguments.
 */
export async function executeAacCommand(): Promise<void> {

    let availableCommands: string[] = await getAacCommandNames();

    const quickPickOptions: QuickPickOptions = {
        canPickMany: false,
    };

    window.showQuickPick(availableCommands, quickPickOptions).then(commandName => {
        if (commandName) {
            getAacCommandArgs(commandName).then(async (commandArguments) => {
                await getCommandArgUserInput(commandArguments);
                execAacShellCommand(commandName, commandArguments).then(output => {
                    outputChannel.appendLine(output);
                    outputChannel.show();
                });
            });
        }
    });
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

    let argumentsWithoutUserResponse: CommandArgument[] = commandArguments.filter(argument => !argument.userResponse);

    if (argumentsWithoutUserResponse.length > 0) {
        let argumentToPromptUserFor = argumentsWithoutUserResponse[0];

        if (argumentToPromptUserFor?.description?.toLowerCase().includes("path")) {
            const dialogBoxOptions: OpenDialogOptions = {
                title: argumentToPromptUserFor.name,
                canSelectMany: false
            };

            let fileUri: Uri[] | undefined = await window.showOpenDialog(dialogBoxOptions);
            argumentToPromptUserFor.userResponse = fileUri ? fileUri[0]?.path : "";
        } else {
            const inputBoxOptions: InputBoxOptions = {
                title: argumentToPromptUserFor.name,
                prompt: argumentToPromptUserFor.description,
            };

            argumentToPromptUserFor.userResponse = await window.showInputBox(inputBoxOptions);
        }
    } else if (argumentsWithoutUserResponse.length > 1) {
        getCommandArgUserInput(commandArguments);
    }
}

async function getAacCommandNames(): Promise<string[]> {
    const aacHelpOutput = await execAacShellCommand("-h");
    return parseTaskNamesFromHelpCommand(aacHelpOutput);
}

/**
 * @returns list of Command arguments
 */
async function getAacCommandArgs(aacCommandName: string): Promise<CommandArgument[]> {
    const aacHelpOutput = await execAacShellCommand(`${aacCommandName} -h`);
    return parseTaskArgsFromHelpCommand(aacHelpOutput);
}

/**
 * Executes AaC commands with arguments.
 * @param command - AaC command name
 * @param commandArgs - command arguments and
 * @returns
 */
async function execAacShellCommand(command: string, commandArgs: CommandArgument[] = []): Promise<string> {
    const commandArgsArray = ["aac", command, ...(commandArgs.map(argument => argument.userResponse))];
    try {
        const { stdout, stderr } = await execShell(commandArgsArray.join(" "), {});
        return stderr.length > 0 ? stderr : stdout;
    } catch (error: any) {
        let errorMessage = error.stderr || error.stdout || "urecognized error";

        outputChannel.appendLine(`Failed to execute AaC command:\n${errorMessage}`);
        outputChannel.show(true);
        throw error;
    }
}

/**
 * Parses command names from the AaC help message.
 * @param aacHelpOutput - the output to parse
 * @returns array of available command names
 */
function parseTaskNamesFromHelpCommand(aacHelpOutput: string): string[] {

    const regExp = /\{(?<commandNames>.*?)\}/;
    const commandNamesMatch = regExp.exec(aacHelpOutput);

    let commandNames: string[] = [];
    if (commandNamesMatch?.groups?.commandNames) {
        commandNames = commandNamesMatch.groups.commandNames.split(",");
    }

    return commandNames;
}

/**
 * Parses argument names and descriptions from command help output
 * @param aacHelpOutput - the output to parse
 * @returns array of CommandArgument objects
 */
function parseTaskArgsFromHelpCommand(commandHelpOutput: string): CommandArgument[] {
    const startRequiredArgsPos = commandHelpOutput.search("positional arguments");
    const startOptionalArgsPos = commandHelpOutput.search("optional arguments");

    const requiredArgsString = commandHelpOutput.substring(startRequiredArgsPos, startOptionalArgsPos);
    const requiredArgs = getArguments(
        requiredArgsString,
        (str: string, descriptionPos: number) => str.substring(0, descriptionPos + 1).trim(),
        (str: string, descriptionPos: number) => str.substring(descriptionPos + 1).trim(),
        "positional arguments:"
    );

    const optionalArgsString = commandHelpOutput.substring(startOptionalArgsPos);
    const optionalArgs = getArguments(
        optionalArgsString,
        (str: string, descriptionPos: number) => descriptionPos >= 0
            ? str.substring(0, descriptionPos + 1).trim()
            : str.trim(),
        (str: string, descriptionPos: number) => descriptionPos >= 0
            ? str.substring(descriptionPos + 1).trim()
            : "",
        "optional arguments:"
    );
    optionalArgs.forEach(arg => arg.optional = true)

    return requiredArgs.concat(optionalArgs);
}

function getArguments(argsString: string, nameExtractor: Function, descriptionExtractor: Function, headline: string) {
    const args: CommandArgument[] = [];

    let name = "";
    let description = "";

    argsString
        .split("\n")
        .filter(it => it.length > 0 && !it.startsWith(headline))
        .forEach((it, _, __) => {
            if (!it.startsWith(" ", 2)) {
                if (name && description) {
                    args.push({
                        name: name.trim(),
                        description: description.trim(),
                    });

                    name = "";
                    description = "";
                }

                const str = it.substring(2);
                const startDescriptionPos = str.search("  ");
                name = nameExtractor(str, startDescriptionPos);
                description = descriptionExtractor(str, startDescriptionPos);
            } else {
                description += " " + it.trim();
            }
        });
    if (name && description) {
        args.push({
            name: name,
            description: description,
        });
    }
    return args;
}
