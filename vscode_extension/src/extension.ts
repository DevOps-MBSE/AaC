import * as fs from "fs";
import { Disposable, ExtensionContext, tasks, workspace } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient/node";
import { AacTaskProvider, execShell } from "./AacTaskProvider";
import { ensureTrue, getConfigurationItem } from "./helpers";

const MIN_REQUIRED_PYTHON_VERSION = "3.9";
const DEFAULT_LSP_SERVER_HOST = "127.0.0.1";
const DEFAULT_LSP_SERVER_PORT = 8080;

let aacTaskProvider: Disposable | undefined;
let aacLspClient: LanguageClient;

export function activate(context: ExtensionContext) {
    aacTaskProvider = tasks.registerTaskProvider(AacTaskProvider.aacType, new AacTaskProvider());
    startLanguageServer(context);
}

function startLanguageServer(context: ExtensionContext) {
    ensureAacToolIsAvailable();
    ensureLspServerIsReady(context);
}

function ensureAacToolIsAvailable(): void {
    const pythonPath = getConfigurationItemFile("pythonPath");
    ensureCorrectPythonVersionIsInstalled(pythonPath);
    ensureCorrectAacVersionIsInstalled(pythonPath);
}

function getConfigurationItemFile(name: string): string {
    const item: string = getConfigurationItem(name);
    ensureTrue(`Cannot start Language Server; '${item}' is not configured!`, item.length > 0);
    ensureTrue(`Cannot use ${item} as it does not exist!`, fs.existsSync(item));
    return item;
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
    const resolve = await execShell(`${pythonPath} -m pip freeze`);
    ensureTrue(`Could not get the installed AaC version.\n${resolve.stderr}`, !resolve.stderr);

    const expectedAacVersion: string = getConfigurationItem("version") ?? "";
    const aacVersionPattern = new RegExp(`aac==${expectedAacVersion}|-e git.*egg=aac`, "ig");
    const actualAacVersion = resolve.stdout.match(aacVersionPattern)?.pop();
    ensureTrue(`The installed aac version is ${actualAacVersion} which is unsupported.`, !!actualAacVersion);
}

function ensureLspServerIsReady(context: ExtensionContext): void {
    const aacPath: string = getConfigurationItemFile("aacPath");
    startLspClient(
        context,
        aacPath,
        getConfigurationItem("lspServerHost") ?? DEFAULT_LSP_SERVER_HOST,
        getConfigurationItem("lspServerPort") ?? DEFAULT_LSP_SERVER_PORT,
    );
}

function startLspClient(context: ExtensionContext, aacPath: string, host: string, port: number): void {
    aacLspClient = new LanguageClient(
        aacPath,
        getServerOptions(aacPath, "start-lsp", "--host", host, "--port", `${port}`),
        getClientOptions()
    );
    context.subscriptions.push(aacLspClient.start());
}

function getServerOptions(command: string, ...args: any[]): ServerOptions {
    return {
        args,
        command,
    };
}

function getClientOptions(): LanguageClientOptions {
    return {
        documentSelector: [
            { scheme: "file", language: "aac" },
            { scheme: "untitled", language: "aac" },
        ],
        outputChannelName: "[aac] Architecture-as-Code Language Server",
        synchronize: {
            fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
        }
    };
}

export function deactivate(): void {
    aacTaskProvider?.dispose();
    shutdownServer();
}

function shutdownServer(): void {
    aacLspClient?.stop();
}
