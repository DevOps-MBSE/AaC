---
layout: default
title: Debugging AaC
parent: Developer's Guide to AaC
nav_order: 1
---

# Debugging AaC In Gitpod

The AaC repository is pre-configured for immediate development in Gitpod environments leverging VSCode, but these steps will work in local
environments as well.

## Opening AaC In Gitpod

If you're going to open the repository in Gitpod, it's fairly straightforward. There are several ways to open the repository in gitpod, the easiest is to click the Gitpod 'Ready-to-Code' button in the readme.
![Gitpod 'Ready-to-Code' button in the repository readme](../../../assets/images/debugging/gitpod_readme_button.png)

If you have the [Gitpod Browser Extension](https://www.gitpod.io/docs/configure/user-settings/browser-extension) then you can simply click the new `Gitpod` button visible in the AaC repository.
![Gitpod browser extension button](../../../assets/images/debugging/gitpod_browser_button.png)

For more information you can check out the [Gitpod documentation](https://www.gitpod.io/docs/introduction/getting-started).

## Debugging the AaC Python Project

The AaC Python project has several debug tasks pre-configured for VSCode in the `.vscode/python.code-workspace` configuration file. You can open the python project in VSCode by opening the VSCode command prompt via the `F1` button, or `function + F1` depending on your operating system, then type 'open' or 'open workspace' to see the `File: Open Workspace from File...`  command option.
![File: Open Workspace from File... option](../../../assets/images/debugging/command_workspace.png)

Once you see the option to open a workspace file, navigate to the top-level `.vscode` file and select the python project configuration.
![Open python project file](../../../assets/images/debugging/select_workspace_python.png)

After the python workspace has been opened, you can select the VSCode debug icon in the left-hand activity bar. You should then be able to run one of the number of AaC commands.
![Run python debugging command](../../../assets/images/debugging/python_debugging.png)

## Debugging the AaC VSCode Project

The AaC Python VSCode Extension project can be run in debug mode via its pre-configured VSCode project in the `.vscode/vscode_extension.code-workspace` file. You can open the VSCode extension project in VSCode by opening the VSCode command prompt via the `F1` button, or `function + F1` depending on your operating system, then type 'open' or 'open workspace' to see the `File: Open Workspace from File...`  command option.
![File: Open Workspace from File... option](../../../assets/images/debugging/command_workspace.png)

Once you see the option to open a workspace file, navigate to the top-level `.vscode` file and select the VSCode extension project configuration.
![Open vscode extension project file](../../../assets/images/debugging/select_workspace_extension.png)

After the VScode extension workspace has been opened, you can open the file `extension.ts` then run debug via `F5` or `function + F5`. You'll see a selection of debug options, choose `VS Code Extension Development` which should then open another tab of Gitpod or instance of VSCode running the extension in debug mode.
![Typescript debug environment](../../../assets/images/debugging/debug_extension.png)

Once you have the debug instance running, you can set a breakpoint in the VSCode extension files and plug away.
