# Architecture-as-Code Secure Installation
In order to support portability of Architecture-as-Code, and to provide a secure, repeatable installation method for AaC users, we have created this one-stop installation package for each release of the AaC python package.

In this package we provide a couple different methods to install AaC and its dependencies, depending on your needs and environment.

## Hash-Verified PyPI Dependencies
When we cut a release of AaC, we'll include a list of the runtime dependencies for AaC and their hash values. When you install via `pip install --require-hashes -r requirements.txt` it will pull the pinned package versions, and verify their hashes for data integrity.

## Air-Gapped Installation
In order to support installation bundles that don't require internet access, we have built [Pip Wheelhouses (Installation Bundles)](https://pip.pypa.io/en/stable/topics/repeatable-installs/) for supported platforms. If don't find support for you platform, please make an issue and we'll address it provided the github actions pipeline is capable of supporting the platform.

In order to install the wheelhouse for you platform