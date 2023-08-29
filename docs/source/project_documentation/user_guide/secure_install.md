# Architecture-as-Code Secure Installation
In order to support portability of Architecture-as-Code, and to provide a secure, repeatable installation method for AaC users, we have created
this one-step installation package for each release of the AaC python package.

In this package we provide a couple different methods to install AaC and its dependencies, depending on your needs and environment.

## Hash-Verified PyPI Dependencies
When we create a release of AaC, we'll include a list of the runtime dependencies for AaC and their hash values. When you install via `pip install --require-hashes -r requirements.txt`
it will pull the pinned package versions, and verify the package's hash value against the value in the requirements file for data integrity. If you prefer to avoid executing the long pip command, you can run the `install_aac_verified_index` script. The installed artifacts will be sourced from PyPI.

### Hash for Linux/macOS
Github's artifact archiver doesn't preserve permissions so you'll have to make the script executable.

```
chmod +x ./install_aac_verified_index.bash
./install_aac_verified_index.bash
```

### Hash for Windows

```
.\install_aac_verified_index.bat
```

## Air-Gapped Installation
For air-gapped installations without access to PyPI, or which may not want to use the indexed artifacts, we provide a PyPI-less (no index) installation method. You can execute `pip install --require-hashes -r requirements.txt --no-index --find-links ./` or the `install_aac_air_gap` script. This mode will verify the hashes of the AaC package and its runtime dependencies, packaged as wheels in the secure installation archive, and then it will install them. **The runtime artifacts are not pulled from PyPI.**

### Air-Gapped for Linux/macOS
Github's artifact archiver doesn't preserve permissions so you'll have to make the script executable.

```
chmod +x ./install_aac_air_gap.bash
./install_aac_air_gap.bash
```

### Air-Gapped for Windows

```
.\install_aac_air_gap.bat
```
