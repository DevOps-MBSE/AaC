import * as fs from "fs";
import { ExtensionContext, workspace } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions, Trace } from "vscode-languageclient/node";
import { assertTrue, execShell, getConfigurationItem, showMessageOnError, getSemanticVersionNumber } from "./helpers";

const MIN_REQUIRED_PYTHON_VERSION = "3.9";

export class AacLanguageServerClient {
    private static instance: AacLanguageServerClient;

    private aacLspClient!: LanguageClient;

    private constructor() { }

    public static getLspClient(): AacLanguageServerClient {
        if (!AacLanguageServerClient.instance) {
            AacLanguageServerClient.instance = new AacLanguageServerClient();
        }
        return AacLanguageServerClient.instance;
    }

    public startLanguageServer(context: ExtensionContext): void {
        this.assertAacToolIsAvailable();
        this.assertLspServerIsReady(context);
    }

    public shutdownServer(): void {
        this.aacLspClient.stop();
    }

    private assertAacToolIsAvailable(): void {
        const pythonPath = this.getConfigurationItemFile("pythonPath");
        this.assertCorrectPythonVersionIsInstalled(pythonPath);
        this.assertCorrectAacVersionIsInstalled(pythonPath);
    }

    private getConfigurationItemFile(name: string): string {
        const item: string = getConfigurationItem(name);
        assertTrue(item.length > 0, `Cannot start Language Server; '${name}' is not configured!`);
        assertTrue(fs.existsSync(item), `Cannot use ${name} as it does not exist!`);
        return item;
    }

    private async assertCorrectPythonVersionIsInstalled(pythonPath: string): Promise<void> {
        const resolve = await execShell(`${pythonPath} --version`, {});

        // Python 2 apparently writes it's version to standard error...
        const versionInStandardError = getSemanticVersionNumber(resolve.stderr);
        assertTrue(!resolve.stderr || !!versionInStandardError, `Could not get the Python version.\n${resolve.stderr}`);

        const pythonVersion = getSemanticVersionNumber(resolve.stdout) ?? versionInStandardError ?? "unknown";
        assertTrue(
            pythonVersion.startsWith(MIN_REQUIRED_PYTHON_VERSION),
            `The AaC tool requires Python ${MIN_REQUIRED_PYTHON_VERSION} or newer; current version is: ${pythonVersion}`,
        );
    }

    private async assertCorrectAacVersionIsInstalled(pythonPath: string): Promise<void> {
        const resolve = await execShell(`${pythonPath} -m pip freeze`);
        assertTrue(!resolve.stderr, `Could not get the installed AaC version.\n${resolve.stderr}`);

        const expectedAacVersion: string = getConfigurationItem("version") ?? "";
        const aacVersionPattern = new RegExp(`aac==${expectedAacVersion}|-e git.*egg=aac`, "ig");
        const actualAacVersion = resolve.stdout.match(aacVersionPattern)?.pop();
        assertTrue(!!actualAacVersion, `The installed aac version is ${actualAacVersion} which is unsupported.`);
    }

    private assertLspServerIsReady(context: ExtensionContext): void {
        const aacPath: string = this.getConfigurationItemFile("aacPath");
        showMessageOnError(() => this.startLspClient(context, aacPath), 'Failed trying to start the server.');
        showMessageOnError(() => this.aacLspClient.onReady(), 'Failed waiting for the server to become ready.');
    }

    private async startLspClient(context: ExtensionContext, aacPath: string): Promise<void> {
        if (this.aacLspClient) { return; }
        this.aacLspClient = new LanguageClient(
            "aac",
            "AaC Language Client",
            this.getServerOptions(aacPath, "start-lsp"),
            this.getClientOptions(),
        );
        this.aacLspClient.trace = Trace.Verbose;
        context.subscriptions.push(this.aacLspClient.start());
    }

    private getServerOptions(command: string, ...args: string[]): ServerOptions {
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
            outputChannelName: "Architecture-as-Code Language Server",
            synchronize: {
                fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
            }
        };
    }

}
