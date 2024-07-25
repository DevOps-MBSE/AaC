# Check

The `check` plugin evaluates an AaC model against the AaC constraints.  The `check` plugin will output any errors that are found.

## Check Command

![Check Command Example](../../images/examples/check-output.PNG)

## Arguments

### AaC File

The AaC file containing the model definition(s) to evaluate for meeting constraints.

## Optional Arguments

### Fail on Warn

The `--fail-on-warn` argument will cause the check command to return a failure if a warning is encountered.  This can be useful in your CI/CD pipeline to ensure that no warnings are present in your model.

### Verbose

The `--verbose` argument will output the results of all constraints evaluated, regardless of the level.  This can be useful for debugging.

![Check Command Verbose Output](../../images/examples/check-verbose-output.png)

## Help

![Check Command Help](../../images/examples/check-h.png)
