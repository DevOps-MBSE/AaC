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
            executeCommandWithArguments(commandName).then((output: string) => {
                outputChannel.appendLine(output);
                outputChannel.show();
             });
        }
    });
}

export async function executeCommandWithArguments(commandName: string): Promise<string> {
    return await getAacCommandArgs(commandName).then(async (commandArguments) => {
        await getCommandArgUserInput(commandArguments);
        return await execAacShellCommand(commandName, commandArguments);
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
    let argumentsWithoutUserResponse: CommandArgument[] = commandArguments
        .filter(argument => !argument.userResponse)
        .filter(argument => !argument.name?.includes("--help"));

    for (let index = 0; index < argumentsWithoutUserResponse.length; ++index) {
        let argumentToPromptUserFor = argumentsWithoutUserResponse[index];
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
    const commandArgsArray = commandArgs
        .filter(argument => argument.userResponse)
        .map(argument => argument.optional ? `${argument.name} ${argument.userResponse}` : argument.userResponse);

    try {
        const { stdout, stderr } = await execShell(["aac", command, ...commandArgsArray].join(" "), {});
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
    const argumentSectionHeader = (name: string) => `${name} arguments:`;
    const requiredArgsHeader = argumentSectionHeader("positional");
    const optionalArgsHeader = argumentSectionHeader("optional");

    const requiredArgsPos = commandHelpOutput.search(requiredArgsHeader) + requiredArgsHeader.length;
    const optionalArgsPos = commandHelpOutput.search(optionalArgsHeader) + optionalArgsHeader.length;

    const requiredArgsString = commandHelpOutput.substring(requiredArgsPos, optionalArgsPos);
    const requiredArgs = getArguments(requiredArgsString);

    const optionalArgsString = commandHelpOutput.substring(optionalArgsPos);
    const optionalArgs = getArguments(optionalArgsString);
    optionalArgs.forEach(arg => {
        arg.name = !arg.name?.includes("--help") ? arg.name?.split(" ")[0] : arg.name;
        arg.optional = true;
    });

    return requiredArgs.concat(optionalArgs);
}

/**
 * Parses the provided section of the help message and extracts command arguments and names.
 *
 * @param argsString - A string containing all the required or optional arguments.
 * @returns A list of required and optional {@link CommandArgument}s.
 */
function getArguments(argsString: string) {
    const args: CommandArgument[] = [];

    let name = "";
    let description = "";

    function addArgument() {
        if (name && description) {
            args.push({
                name: name.trim(),
                description: description.trim(),
            });

            name = "";
            description = "";
        }
    }

    argsString
        .split("\n")
        .filter(it => it.length > 0)
        .forEach((it, _, __) => {
            if (!it.startsWith(" ", 2)) {
                addArgument();

                const str = it.substring(2);
                const startDescriptionPos = str.search("  ");

                name = startDescriptionPos >= 0
                    ? str.substring(0, startDescriptionPos + 1)
                    : str.trim();
                description = startDescriptionPos >= 0
                    ? str.substring(startDescriptionPos + 1)
                    : "";
            } else {
                description += " " + it.trim();
            }
        });
    addArgument();
    return args;
}
