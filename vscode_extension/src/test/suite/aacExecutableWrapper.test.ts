import * as assert from "assert";

import * as aacWrapper from "../../aacExecutableWrapper";
import * as helpers from "../../helpers";

suite("AaC Executable Wrapper Test Suite", () => {
    test("we can get version of aac tool", async () => {
        await aacWrapper.getAaCVersion()
            .then(value => assert.strictEqual(value, helpers.getConfigurationItem("version")))
            .catch(reason => assert.fail(reason));
    });

    test("we can execute a command with no arguments", async () => {
        await aacWrapper.executeCommandWithArguments("version")
            .then((output: string) => assert.ok(output.includes(helpers.getConfigurationItem("version"))))
            .catch(reason => assert.fail(reason));
    });
});
