import { ImportMock } from "ts-mock-imports";

import * as assert from "assert";
import * as vscode from "vscode";

import * as aacWrapper from "../../aacExecutableWrapper";
import * as helpers from "../../helpers";

import * as io from "./helpers/io";

suite("AaC Executable Wrapper Test Suite", () => {
    test("we can get version of aac tool", async () => {
        await aacWrapper.getAaCVersion().then(value => assert.strictEqual(value, helpers.getConfigurationItem("version")));
    });

    test("we can execute a command with no arguments", async () => {
        await aacWrapper.executeCommandWithArguments("version")
            .then((output: string) => assert.ok(output.includes(helpers.getConfigurationItem("version"))))
            .catch(reason => assert.fail(reason));
    });

    test("we can execute a command with only required arguments", async () => {
        const filespec = "test.yaml";
        const model = "\
data:\n\
  name: Person\n\
  fields:\n\
  - name: name\n\
    type: string\n\
  required:\n\
  - name\n";

        io.withTestFile(filespec, model, async () => {
            const stub = ImportMock.mockFunction(vscode.window, "showOpenDialog", vscode.Uri.parse(filespec));
            await aacWrapper.executeCommandWithArguments("validate")
                .then((output: string) => assert.ok(output.includes(`${filespec} is valid`)))
                .catch(reason => assert.fail(reason));
            stub.restore();
        });
    });
});
