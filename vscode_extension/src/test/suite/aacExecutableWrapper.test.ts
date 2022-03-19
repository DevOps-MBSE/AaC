import * as assert from "assert";

import * as aacWrapper from "../../aacExecutableWrapper";
import * as helpers from "../../helpers";

suite("AaC Executable Wrapper Test Suite", () => {
    test("we can get version of aac tool", () => {
        aacWrapper.getAaCVersion().then((value) => {
            assert.strictEqual(value, helpers.getConfigurationItem("version"));
            assert.fail(`this should fail! -- value is: ${value}`);
        });
    });

    test("we can execute a command with no arguments", () => {
        aacWrapper.executeCommandWithArguments("version")
            .then((output: string) => output.includes(helpers.getConfigurationItem("version")))
            .catch(reason => assert.fail(reason));
    });

    test("we can execute a command with only required arguments", () => {
        aacWrapper.executeCommandWithArguments("validate")
            .then((output: string) => output.includes("is valid"))
            .catch(reason => assert.fail(reason));
    });
});
