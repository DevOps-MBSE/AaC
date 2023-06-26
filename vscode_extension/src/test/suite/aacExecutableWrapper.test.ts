import * as assert from "assert";

import * as aacWrapper from "../../aacExecutableWrapper";

suite("AaC Executable Wrapper Test Suite", () => {
    test("it should execute a command with no arguments", async () => {
        const versionCommand = {
            name: "version",
            description: "",
            arguments: [],
        };

        await aacWrapper.executeCommandWithArguments(versionCommand)
            .then((output: string) => {
                // Leaving the minor version out of the test.
                const searchString = "0.2.";
                assert.strictEqual(output.includes(searchString), true, `'${searchString}' not found in ${output}`);
            });
    });

    test("it should execute the help command", async () => {
        const helpDumpCommand = {
            name: "help-dump",
            description: "",
            arguments: [],
        };


        await aacWrapper.executeCommandWithArguments(helpDumpCommand)
            .then((output: string) => {
                const searchString = "Validate the AaC definition file";
                assert.strictEqual(output.includes(searchString), true, `'${searchString}' not found in ${output}`);
            });
    }).timeout(20000);
});
