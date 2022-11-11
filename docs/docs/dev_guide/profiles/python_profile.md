---
layout: default
title: Python Profile Setup and Justification
parent: Developer's Guide to AaC
nav_order: 1
---

# Profile (Python) Setup and Justification

## Profile Description

`profile` is another deterministic profiler. There are a lot of similaarities to the `cProfile` however, this profiler has a significant amount of overhead and this profiler is pure python based. Therefore if you are needing to extend the profiler this can be done with this package.

>*_NOTE: This profiler is a more advanced version of `cProfile` and has more extensibility and overhead that can be utilized. Majority of cases can be achieved with the `cProfile` package. 

## Getting Started

To get started using the `profile` package you will need to import this into the plugin that is being developed, new or existing.

To do so just use the import statement to bring it in:

```python
import profile
```

To enable the `profile` package is a little more complicated than the `cProfile` conterpart.
`profile` does not support using a Context Manager so the wrapping around the activity will be a little more work:

```python

""" Run Comamnd for profile to run a command within the plugin code """
profile.run(command, filename=None, sort=- 1)

""" This command is similar to run() except that it accepts globals and locals definitions that are supplied and passed through the command being executed. """
profile.runctx(command, globals, locals, filename=None, sort=- 1)

""" The Profile() class. This is really only needed for more precise controls over the profiling being done
than what the cProfile.run() method can provide. """
class profile.Profile(timer=None, timeunit=0.0, subcalls=True, builtins=True)
```
