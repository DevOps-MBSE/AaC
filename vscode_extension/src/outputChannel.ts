import { window, OutputChannel } from "vscode";

let _extension_output_channel: OutputChannel;

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

    if (!_extension_output_channel) {
        _extension_output_channel = window.createOutputChannel('Architecture-as-Code');
    }
    return _extension_output_channel;
}