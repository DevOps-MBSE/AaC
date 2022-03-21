import * as fs from "fs";

/**
 * Create `filespec` and then run the specified `action`, then delete `filespec`.
 *
 * @param filespec - The name of the file to write.
 * @param data - The data to be written to the file.
 * @param action - A thunk to run after the file has been created.
 */
export function withTestFileSync(filespec: string, data: string, action: Function): void {
    const cleanUpFile = () => {
        if (fs.existsSync(filespec)) {
            fs.rmSync(filespec);
        }
    };

    try {
        fs.writeFileSync(filespec, data);
        action();
        cleanUpFile();
    } catch (error) {
        cleanUpFile();
    }
}

/**
 * Create `filespec` and then await the specified `action`, then delete `filespec`.
 *
 * @param filespec - The name of the file to write.
 * @param data - The data to be written to the file.
 * @param action - An asynchronous thunk to run after the file has been created.
 */
export async function withTestFile(filespec: string, data: string, action: Function) {
    const cleanUpFile = () => {
        if (fs.existsSync(filespec)) {
            fs.rmSync(filespec);
        }
    };

    try {
        fs.writeFileSync(filespec, data);
        await action();
        cleanUpFile();
    } catch (error) {
        cleanUpFile();
    }
}
