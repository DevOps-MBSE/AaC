import { exec, ExecOptions } from "child_process";
import { StringDecoder } from "string_decoder";

/**
 * Execute a shell `command` on the underlying system.
 *
 * WARNING: Make sure to sanitize any user-provided data before calling this function!
 *
 * @param command - The command to be executed.
 * @param options - Optionally any ExecOptions that should be used when executing the `command`.
 *
 * @returns A `Promise` with the standard output (`stdout`) and standard error (`stderr`) produced by running `command`.
 */
 export function execShell(command: string, options?: ExecOptions): Promise<{ stdout: string; stderr: string }> {
    return new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
        exec(command, options, (error, stdout, stderr) => {
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
