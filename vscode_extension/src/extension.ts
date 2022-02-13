import * as fs from "fs";
import { Disposable, ExtensionContext, tasks, window } from "vscode";
import { LanguageClient } from "vscode-languageclient/node";
import { AacTaskProvider, execShell } from "./AacTaskProvider";
import { ensureTrue, getConfigurationItem } from "./helpers";

const MIN_REQUIRED_PYTHON_VERSION = "3.9";

let aacTaskProvider: Disposable | undefined;
let aacLspClient: LanguageClient | undefined;

export function activate(context: ExtensionContext) {
    aacTaskProvider = tasks.registerTaskProvider(AacTaskProvider.aacType, new AacTaskProvider());
    startLanguageServer(context)
}

function startLanguageServer(_context: ExtensionContext) {
    ensureAacToolIsAvailable();
    aacLspClient?.start();
}

function ensureAacToolIsAvailable(): void {
    const pythonPath = getPython3Path();
    ensureCorrectPythonVersionIsInstalled(pythonPath);
    ensureCorrectAacVersionIsInstalled(pythonPath);

    // TODO: Actually start the server
}

function getPython3Path(): string {
    const pythonPath: string = getConfigurationItem("pythonPath") ?? "";
    ensureTrue("Cannot start Language Server; 'pythonPath' is not configured!", pythonPath.length > 0)
    ensureTrue(`Cannot use ${pythonPath} as it does not exist!`, fs.existsSync(pythonPath))

    return pythonPath;
}

async function ensureCorrectPythonVersionIsInstalled(pythonPath: string): Promise<void> {
    const resolve = await execShell(`${pythonPath} --version`, {});
    ensureTrue(`Could not get the Python version.\n${resolve.stderr}`, !resolve.stderr);

    const pythonVersion = resolve.stdout.match(/\d+\.\d+\.\d+/)?.pop() ?? "unknown";
    ensureTrue(
        `The AaC tool requires Python ${MIN_REQUIRED_PYTHON_VERSION} or newer; current version is: ${pythonVersion}`,
        pythonVersion.startsWith(MIN_REQUIRED_PYTHON_VERSION)
    );
}

async function ensureCorrectAacVersionIsInstalled(pythonPath: string): Promise<void> {
    const resolve = await execShell(`${pythonPath} -m pip freeze`)
    ensureTrue(`Could not get the installed AaC version.\n${resolve.stderr}`, !resolve.stderr);

    const expectedAacVersion: string = getConfigurationItem("version") ?? "";
    const aacVersionPattern = new RegExp(`aac==${expectedAacVersion}|-e git.*egg=aac`, "ig");
    const actualAacVersion = resolve.stdout.match(aacVersionPattern)?.pop();
    ensureTrue(`The installed aac version is ${actualAacVersion} which is unsupported.`, !!actualAacVersion);
}

export function deactivate(): void {
    aacTaskProvider?.dispose();
    aacLspClient?.stop();
}
