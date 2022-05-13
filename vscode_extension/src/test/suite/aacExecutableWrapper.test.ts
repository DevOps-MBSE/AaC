import * as assert from "assert";

import * as aacWrapper from "../../aacExecutableWrapper";
import * as helpers from "../../helpers";
import * as configuration from "../../configuration";

suite("AaC Executable Wrapper Test Suite", () => {
    test("it should get the version of the aac tool", async () => {
        await aacWrapper.getAaCVersion()
            .then(value => assert.strictEqual(value, configuration.getConfigurationItem("version")))
            .catch(reason => assert.fail(reason));
    });

    test("it should execute a command with no arguments", async () => {
        const versionCommand = {
            name: "version",
            description: "",
            arguments: [],
        };

        await aacWrapper.executeCommandWithArguments(versionCommand)
            .then((output: string) => assert.ok(output.includes(configuration.getConfigurationItem("version"))))
            .catch(reason => assert.fail(reason));
    });
});
