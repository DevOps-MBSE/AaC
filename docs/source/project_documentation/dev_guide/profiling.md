# cProfile and Profile Setup and Justification

## cProfile Description

`cProfile`, like `profile` is a deterministic profiler. Unlike the Python-backed `Profile`, `cProfile` is backed by the `lsprof` , and is a `C` extension.
This profiler is the one that comes recommended for most use-cases as it has reasonable overhead and works really well for some long running programs.

With this in mind `cProfile` is quite efficient and is able to run quickly allowing for quick and easy profiling of plugin code. However, it may not be available in all distributions as it requires platform-specific compiled c binaries.

The official Python Profiling Documentation can be found [here.](https://docs.python.org/3/library/profile.html)

## Getting Started with cProfile

To get started using the `cProfile` profiler you will need to import the profile into a new or existing plugin.

```python
import cProfile
```

To enable this profiler you can add the following code to your plugin to profile against any performance or other issues that may be suspected:

```python
# This is with using the `cProfile` profiler to test the version plugin.

import cProfile
import pstats
from pstats import SortKey
from aac.plugins.version.version_impl import version

return_value = None
with cProfile.Profile() as pr:
    return_value = version()
ps = pstats.Stats(pr).sort_stats(SortKey.CUMULATIVE) # Keep this outside the context manager scope to prevent pollution in the profiler.
ps.print_stats(10) # Print the top 10 calls
return return_value
```

When you don't sort your results you can get a lot of noise from some functions and methods that are being called which can add to the confusion of what the plugin is doing. 

## Profile Description

`profile` is another deterministic profiler. There are a lot of similarities to the `cProfile` however, it has a considerable overhead when compared to `cProfile` and it is written in Python. Therefore, if you need to extend the profiler, you can accomplish that with this package more easily.

It is recommended to use `cProfile` for the majority of use-cases, and to use `profile` for extensibility and when there is less consideration for overhead or performance.


### Getting Started with Profile

To get started using the `profile` package you will need to import this into the plugin that is being developed, new or existing.

```python
import profile
```

To enable the `profile` package is a little more complicated than the `cProfile` conterpart.
`profile` does not support using a Context Manager so the wrapping around the activity will be a little more work:

```python
# Profile an AaC command within the plugin code
profile.run(command, filename=None, sort=- 1)

# This command is similar to run() except that it accepts globals and locals definitions that are supplied and passed # through the command being executed.
profile.runctx(command, globals, locals, filename=None, sort=- 1)

# The Profile() class. This is only needed for more precise control over the profiling being done
class profile.Profile(timer=None, timeunit=0.0, subcalls=True, builtins=True)
```
