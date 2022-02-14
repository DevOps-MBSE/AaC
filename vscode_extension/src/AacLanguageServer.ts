import * as fs from "fs";
import { ExtensionContext, workspace } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient/node";
import { execShell } from "./AacTaskProvider";
import { ensureTrue, getConfigurationItem } from "./helpers";

const MIN_REQUIRED_PYTHON_VERSION = "3.9";
const DEFAULT_LSP_SERVER_HOST = "127.0.0.1";
const DEFAULT_LSP_SERVER_PORT = 8080;

export class AacLanguageServerClient {
    private static instance: AacLanguageServerClient;

    private aacLspClient!: LanguageClient;

    private constructor() { }

    public static makeLspClient(): AacLanguageServerClient {
        if (!AacLanguageServerClient.instance) {
            AacLanguageServerClient.instance = new AacLanguageServerClient();
        }
        return AacLanguageServerClient.instance;
    }

    public startLanguageServer(context: ExtensionContext): void {
        this.ensureAacToolIsAvailable();
        this.ensureLspServerIsReady(context);
    }

    public shutdownServer(): void {
        this.aacLspClient.stop();
    }

    private ensureAacToolIsAvailable(): void {
        const pythonPath = this.getConfigurationItemFile("pythonPath");
        this.ensureCorrectPythonVersionIsInstalled(pythonPath);
        this.ensureCorrectAacVersionIsInstalled(pythonPath);
    }

    private getConfigurationItemFile(name: string): string {
        const item: string = getConfigurationItem(name);
        ensureTrue(`Cannot start Language Server; '${item}' is not configured!`, item.length > 0);
        ensureTrue(`Cannot use ${item} as it does not exist!`, fs.existsSync(item));
        return item;
    }

    private async ensureCorrectPythonVersionIsInstalled(pythonPath: string): Promise<void> {
        const resolve = await execShell(`${pythonPath} --version`, {});
        ensureTrue(`Could not get the Python version.\n${resolve.stderr}`, !resolve.stderr);

        const pythonVersion = resolve.stdout.match(/\d+\.\d+\.\d+/)?.pop() ?? "unknown";
        ensureTrue(
            `The AaC tool requires Python ${MIN_REQUIRED_PYTHON_VERSION} or newer; current version is: ${pythonVersion}`,
            pythonVersion.startsWith(MIN_REQUIRED_PYTHON_VERSION)
        );
    }

    private async ensureCorrectAacVersionIsInstalled(pythonPath: string): Promise<void> {
        const resolve = await execShell(`${pythonPath} -m pip freeze`);
        ensureTrue(`Could not get the installed AaC version.\n${resolve.stderr}`, !resolve.stderr);

        const expectedAacVersion: string = getConfigurationItem("version") ?? "";
        const aacVersionPattern = new RegExp(`aac==${expectedAacVersion}|-e git.*egg=aac`, "ig");
        const actualAacVersion = resolve.stdout.match(aacVersionPattern)?.pop();
        ensureTrue(`The installed aac version is ${actualAacVersion} which is unsupported.`, !!actualAacVersion);
    }

    private ensureLspServerIsReady(context: ExtensionContext): void {
        const aacPath: string = this.getConfigurationItemFile("aacPath");
        this.startLspClient(
            context,
            aacPath,
            getConfigurationItem("lspServerHost") ?? DEFAULT_LSP_SERVER_HOST,
            getConfigurationItem("lspServerPort") ?? DEFAULT_LSP_SERVER_PORT,
        );
    }

    private startLspClient(context: ExtensionContext, aacPath: string, host: string, port: number): void {
        this.aacLspClient = new LanguageClient(
            aacPath,
            this.getServerOptions(aacPath, "start-lsp", "--host", host, "--port", `${port}`),
            this.getClientOptions()
        );
        context.subscriptions.push(this.aacLspClient.start());
    }

    private getServerOptions(command: string, ...args: any[]): ServerOptions {
        return {
            args,
            command,
        };
    }

    private getClientOptions(): LanguageClientOptions {
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

}