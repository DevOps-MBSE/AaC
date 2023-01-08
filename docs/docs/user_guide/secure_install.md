---
layout: default
title: Secure Install
parent: User's Guide to AaC
nav_order: 1x
---

# Architecture-as-Code Secure Installation
In order to support portability of Architecture-as-Code, and to provide a secure, repeatable installation method for AaC users, we have created
this one-stop installation package for each release of the AaC python package.

In this package we provide a couple different methods to install AaC and its dependencies, depending on your needs and environment.

## Hash-Verified PyPI Dependencies
When we create a release of AaC, we'll include a list of the runtime dependencies for AaC and their hash values. When you install via `pip install --require-hashes -r requirements.txt`
it will pull the pinned package versions, and verify the package's hash value against the value in the requirements file for data integrity. If you prefer to avoid executing the long pip command, you can run the `install_aac_verified_index` script. The installed artifacts will be sourced from PyPI.


### Linux/macOS
Github's artifact archiver doesn't preserve permissions so you'll have to make the script executable.

```
chmod +x ./install_aac_verified_index.bash
./install_aac_verified_index.bash
```

### Windows

```
.\install_aac_verified_index.bat
```

## Air-Gapped Installation
For air-gapped installations without access to PyPI, or which may not want to use the indexed artifacts, we provide a PyPI-less (no index) installation method. You can execute `pip install --require-hashes -r requirements.txt --no-index --find-links ./` or the `install_aac_air_gap` script. This mode will verify the hashes of the AaC and its runtime dependencies, packaged as wheels, and then install them -- the runtime artifacts are not pulled from PyPI.

### Linux/macOS
Github's artifact archiver doesn't preserve permissions so you'll have to make the script executable.

```
chmod +x ./install_aac_air_gap.bash
./install_aac_air_gap.bash
```

### Windows

```
.\install_aac_air_gap.bat
```
