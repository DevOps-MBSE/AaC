import * as fs from "fs";
import { ExtensionContext, window, workspace } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions, Trace } from "vscode-languageclient/node";
import { ensureTrue, execShell, getConfigurationItem, showMessageOnError } from "./helpers";

const MIN_REQUIRED_PYTHON_VERSION = "3.9";

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
        ensureTrue(item.length > 0, `Cannot start Language Server; '${item}' is not configured!`);
        ensureTrue(fs.existsSync(item), `Cannot use ${item} as it does not exist!`);
        return item;
    }

    private async ensureCorrectPythonVersionIsInstalled(pythonPath: string): Promise<void> {
        const resolve = await execShell(`${pythonPath} --version`, {});
        ensureTrue(!resolve.stderr, `Could not get the Python version.\n${resolve.stderr}`);

        const pythonVersion = resolve.stdout.match(/\d+\.\d+\.\d+/)?.pop() ?? "unknown";
        ensureTrue(
            pythonVersion.startsWith(MIN_REQUIRED_PYTHON_VERSION),
            `The AaC tool requires Python ${MIN_REQUIRED_PYTHON_VERSION} or newer; current version is: ${pythonVersion}`,
        );
    }

    private async ensureCorrectAacVersionIsInstalled(pythonPath: string): Promise<void> {
        const resolve = await execShell(`${pythonPath} -m pip freeze`);
        ensureTrue(!resolve.stderr, `Could not get the installed AaC version.\n${resolve.stderr}`);

        const expectedAacVersion: string = getConfigurationItem("version") ?? "";
        const aacVersionPattern = new RegExp(`aac==${expectedAacVersion}|-e git.*egg=aac`, "ig");
        const actualAacVersion = resolve.stdout.match(aacVersionPattern)?.pop();
        ensureTrue(!!actualAacVersion, `The installed aac version is ${actualAacVersion} which is unsupported.`);
    }

    private ensureLspServerIsReady(context: ExtensionContext): void {
        const aacPath: string = this.getConfigurationItemFile("aacPath");
        showMessageOnError(() => this.startLspClient(context, aacPath), 'Failed trying to start the server.');
        showMessageOnError(() => this.aacLspClient.onReady(), 'Failed waiting for the server to become ready.');
    }

    private async startLspClient(context: ExtensionContext, aacPath: string): Promise<void> {
        if (this.aacLspClient) { return; }
        this.aacLspClient = new LanguageClient(
            "aac",
            "AaC Language Client",
            this.getProdServerOptions(aacPath, "start-lsp"),
            this.getClientOptions(),
        );
        this.aacLspClient.trace = Trace.Verbose;
        context.subscriptions.push(this.aacLspClient.start());
    }

    private getProdServerOptions(command: string, ...args: string[]): ServerOptions {
        return {
            args,
            command,
        };
    }

    private getClientOptions(): LanguageClientOptions {
        return {
            documentSelector: [
                { scheme: "file", language: "aac", pattern: "**/*.aac" },
                { scheme: "file", language: "aac", pattern: "**/*.yaml" },
            ],
            diagnosticCollectionName: "aac",
            outputChannelName: "Architecture-as-Code",
            synchronize: {
                fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
            }
        };
    }

}
