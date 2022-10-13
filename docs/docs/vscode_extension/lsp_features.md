---
layout: default
title: AaC LSP Features
nav_order: 3
parent: AaC VSCode Extension
---

# AaC LSP Features

The AaC Language LSP server implementation is still a work-in-progress but that
doesn't mean that it doesn't already provide useful features. The LSP
implementation is intended to bring standard IDE features to the AaC language so
that system modelers can obtain benefits provided by creating systems in an IDE.

All the features described here are available "out of the box" and no extra
configuration is required aside from the initial configuration described in the
[setup guide](/docs/vscode_extension).

## Basic Completion (WIP)

Code completion is still heavily in development, but there is currently a very
basic implementation that provides valid definition names as suggestions when it
detects the modeler is defining a reference to a definition.

The code completion box is available whenever `type: ` is entered in an AaC file.

![Example of completion](/assets/images/vscode_extension/example-code-completion.png)

If you would like code completion outside of this, VSCode provides code
completion that is not context-specific you can simply press `Ctrl-SPC` on
Windows/Linux or `Command-SPC` on Mac.

## Hover

The AaC LSP implementation provides so-called "hover" functionality as a way to
allow modelers to view a definition without having to navigate to the specific
definition.

To activate this functionality you only need hover over the name of a recognized
AaC definition, that definition will be shown in a popup box.

![Example of hover](/assets/images/vscode_extension/example-hover.png)

## Go to Definition

The LSP implementation provides the ability to navigate to a definition with a
keyboard shortcut or a couple clicks. The ability to navigate to the file in
which an AaC Definition is expressed is beneficial for scenarios where
[hovering](#hover) doesn't give you enough information at once or when you need
to modify a definition but don't necessarily want to search the filesystem for
it.

To activate this functionality you need to select the name of a recognized AaC
definition and either press the "F12" key or right-click and select the "Go to
Definition" option.

![Example of go to definition](/assets/images/vscode_extension/example-go-to-definition.png)

After completing that, you will be taken to the definition:

![After executing go to definition action](/assets/images/vscode_extension/example-go-to-definition-afterwards.png)

## Go to References

The LSP implementation provides the ability to navigate to any reference to a
specific definition in your project. This is useful in cases where you need to
update a particular usage of the definition in a large project that is spread
across several files.

To activate this functionality you need to select the name of a recognized AaC
definition and either press "Shift-F12" on Windows/Linux or "⇧F12" on Mac or
right-click and select the "Go to References" option.

![Example of go to references](/assets/images/vscode_extension/example-go-to-references.png)

After completing that, you will see a popup with every reference to the selected
definition in your project:


![Select the reference to navigate to](/assets/images/vscode_extension/example-go-to-references-picker.png)

Upon selecting one of those definitions, you will be taken to it:

![After selecting the reference to navigate to](/assets/images/vscode_extension/example-go-to-references-afterwards.png)

## Find All References

The LSP implementation provides the ability to display a list of every reference
to a specific definition in your project. This becomes particularly benefitial
when you have a large project that is spread across several files and you'd like
to see where it's used.

To activate this functionality you need to select the name of a recognized AaC
definition and either press "Alt-F12" on Windows/Linux or "⌥⇧F12" on Mac or
right-click and select the "Go to References" option.

![Example of find references](/assets/images/vscode_extension/example-find-references.png)

After completing that, you will see a sidebar with every reference to the
selected definition:

![After executing find all references](/assets/images/vscode_extension/example-find-references-afterwards.png)

## Rename

The LSP implementation provides the ability to rename a definition and update
every reference to that definition in your project. This is benefitial when you
have a large project that is spread across several files and you'd like to
change the name of a definition without having to manually update the name
everywhere it's used.

To activate this functionality you need to select the name of a recognized AaC
definition and either press "F2" or right-click and select the "Rename Symbol"
option.

![Example of rename](/assets/images/vscode_extension/example-rename.png)

After completing that, you will be prompted for a new name - enter the new name
and press "Enter".

![Give the definition a new name](/assets/images/vscode_extension/example-rename-new-name.png)

Once complete, you can view all references to see that the new name has been updated:

![After executing rename](/assets/images/vscode_extension/example-rename-afterwards.png)

## Symantic Highlighting

The LSP implementation provides semantic highlighting to enhance the user
experience with customized syntax coloring for specific AaC items. Without
semantic highlighting, all AaC definitions will look the same like standard YAML
but with semantic highlighting observant users can distinguish various types of
definitions by their syntax coloring. For example, depending on your chosen
theme, an enum definition will have one color compared to a schema definition,
and so on.


![TODO: Add image showing no semantic highlighting]()
![TODO: Add image showing semantic highlighting]()
