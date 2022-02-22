import * as cp from 'child_process';
import { StringDecoder } from "string_decoder";
import { workspace } from "vscode";

export function ensure(test: () => boolean, failureMessage: string): void {
    if (!test()) {
        throw new Error(failureMessage);
    }
}

export function ensureTrue(test: boolean, failureMessage: string): void {
    ensure(() => test, failureMessage);
}

export function showMessageOnError(action: () => any, failureMessage: string): any {
    try {
        return action();
    } catch (onFailure) {
        throw new Error(`${failureMessage}\n${onFailure}`);
    }
}

export function getConfigurationItem(name: string): any {
    return workspace.getConfiguration().get(`aac.${name}`) ?? null;
}

export function execShell(command: string, options?: cp.ExecOptions): Promise<{ stdout: string; stderr: string }> {
    return new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
        cp.exec(command, options, (error, stdout, stderr) => {
            stdout = convertBufferToString(stdout);
            stderr = convertBufferToString(stderr);
            if (error) {
                reject({ error, stdout, stderr });
            }
            resolve({ stdout, stderr });
        });
    });
}

function convertBufferToString(arg: string | Buffer, encoding: BufferEncoding = "utf-8"): string {
    if (Buffer.isBuffer(arg)) {
        return new StringDecoder(encoding).write(Buffer.from(arg));
    }
    return <string>arg;
}
