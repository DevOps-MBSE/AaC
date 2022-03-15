import { window, OutputChannel } from "vscode";

let extensionOutputChannel: OutputChannel;

/**
 * @returns vscode.OutputChannel for AaC extension output to the VSCode Output Panel.
 *
 * @example
 * Sets the content of an output panel to `Hello!`:
 * ```ts
 *  let stringMessage = "Hello!"
 *  const outputChannel = getOutputChannel();
 *  outputChannel.appendLine(stringMessage);
 *  outputChannel.show(true);
 * ```
 * @see {@link https://code.visualstudio.com/api/references/vscode-api#OutputChannel | VSCode OutputChannel API documentation}
 */
 export function getOutputChannel(): OutputChannel {

    if (!extensionOutputChannel) {
        extensionOutputChannel = window.createOutputChannel('Architecture-as-Code');
    }
    return extensionOutputChannel;
}