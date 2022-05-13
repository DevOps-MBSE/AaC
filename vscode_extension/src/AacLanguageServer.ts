import * as fs from "fs";
import * as net from "net";

import { ExtensionContext, window, workspace } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions, StreamInfo, Trace } from "vscode-languageclient/node";
import { getConfigurationItem } from "./configuration";
import { execShell } from "./shell";
import { assertTrue, showMessageOnError, getSemanticVersionNumber } from "./helpers";

enum LspServerMode {
    io = "IO",
    tcp = "TCP",
}

const MIN_REQUIRED_PYTHON_VERSION = "3.9";
const DEFAULT_LSP_SERVER_MODE = LspServerMode.io;

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

        showMessageOnError(() => this.startLspClient(context), "Failed trying to start the server.");
        this.onClientReady();
    }

    public shutdownServer(): void {
        this.aacLspClient.stop();
    }

    private assertAacToolIsAvailable(): void {
        const pythonPath = this.getConfigurationItemFile("pythonPath");
        this.assertCorrectPythonVersionIsInstalled(pythonPath);
        this.assertCorrectAacVersionIsInstalled(pythonPath);
    }

    private onClientReady(): any {
        try {
            this.aacLspClient.onReady();

            workspace.findFiles("**/*.aac").then(files => {
                for (const fileIndex in files) {
                    const file = files[fileIndex];
                    workspace.openTextDocument(file.path);
                }
            });
        } catch (onFailure) {
            window.showErrorMessage(`Failed waiting for the server to become ready.\n${onFailure}`);
        }
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

    private async startLspClient(context: ExtensionContext): Promise<void> {
        if (this.aacLspClient) { return; }
        this.aacLspClient = new LanguageClient(
            "aac",
            "AaC Language Client",
            this.getServerOptions(),
            this.getClientOptions(),
        );
        this.aacLspClient.trace = Trace.Verbose;
        context.subscriptions.push(this.aacLspClient.start());
    }

    private getServerOptions(): ServerOptions | (() => Promise<StreamInfo>) {
        const lspServerMode = getConfigurationItem("lsp.serverMode");
        if (lspServerMode === LspServerMode.tcp) {
            return this.getTcpServerOptions();
        }

        assertTrue(
            lspServerMode === DEFAULT_LSP_SERVER_MODE,
            `Unsupported LSP server mode selected: ${lspServerMode}. Defaulting to ${DEFAULT_LSP_SERVER_MODE}.`
        );
        return this.getIoServerOptions();
    }

    private getIoServerOptions(): ServerOptions {
        return {
            command: this.getConfigurationItemFile("aacPath"),
            args: ["start-lsp-io"]
        };
    }

    private getTcpServerOptions(): (() => Promise<StreamInfo>) {
        const host = getConfigurationItem("lsp.tcp.host");
        const port = getConfigurationItem("lsp.tcp.port");

        const socket = net.connect(port, host);
        socket.addListener("error", (err: Error) => {
            let message = `Error connecting to server at ${host}:${port}. `;
            message += (err.message.includes("ECONNREFUSED")) ? "Is the server running?" : err.message;
            window.showErrorMessage(message);
        });

        return () => Promise.resolve({
            writer: socket,
            reader: socket,
        });
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
                fileEvents: workspace.createFileSystemWatcher("**/.aac")
            }
        };
    }

}