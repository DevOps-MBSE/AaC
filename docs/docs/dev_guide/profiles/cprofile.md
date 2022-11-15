---
layout: default
title: cProfile and Profile Setup and Justification
parent: Developer's Guide to AaC
nav_order: 2
---

# cProfile and Profile Setup and Justification

## cProfile Description

`cProfile`, like `profile` is a deterministic profiler. Unlike the Python-backed `Profile`, `cProfile` is backed by the `lsprof` , and is a `C` extension.
This profiler is the one that comes recommended for most use-cases as it has reasonable overhead and works really well for some long running programs.

With this in mind `cProfile` is quite efficient and is able to run quickly allowing for quick and easy profiling of plugin code. However, it may not be available in all distributions as it requires platform-specific compiled c binaries.

The official Python Profiling Documentation can be found [here.](https://docs.python.org/3/library/profile.html)

## Getting Started with cProfile

To get started using the `cProfile` profiler you will need to import the profile into a new or existing plugin.

If you are using `cProfile` this can be done with an import:

```python
import cProfile
```

To enable this profiler you can run the following commands against this class:

```python
""" This is with using the `cProfile` profiler within a ContextManager Object. """

import cProfile
import pstats
from pstats import SortKey
return_value = None
with cProfile.Profile() as pr:
    with plugin_result(plugin_name, _validate) as result:
        return_value = result
ps = pstats.Stats(pr).sort_stats(SortKey.CUMULATIVE) # Keep this outside the context manager scope to prevent pollution in the profiler.
ps.print_stats(10) # Print the top 10 calls
return return_value
```

So lets break this down a bit:
When you don't sort your results you can get a lot of noise from some functions and methods that are being called and can really
disorient and add to the confusion of what is going on with the plugin. The above code was run for the `gen_design_doc_impl.py` file
and within the results as seen with `ps.print_stats(10)` we are filtering the top ten sorted lines.

Through the sort function, and filtering the sort you can see the heavy offenders of the plugin that is being profiled.

The output from this run will have something similar to the below:

```bash
aac gen-design-doc ./model/alarm_clock/alarm_clock.yaml ../../../temp/
         4040225 function calls (3966008 primitive calls) in 1.194 seconds

   Ordered by: internal time
   List reduced from 1186 to 10 due to restriction <10>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    19692    0.085    0.000    0.085    0.000 /Users/username/venvs/AaC/python/src/aac/lang/language_context.py:361(<listcomp>)
   107541    0.080    0.000    0.083    0.000 /Users/username/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/reader.py:99(forward)
     8986    0.062    0.000    0.062    0.000 {method 'flush' of '_io.TextIOWrapper' objects}
     8489    0.054    0.000    0.219    0.000 /Users/username/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/scanner.py:1270(scan_plain)
   452287    0.047    0.000    0.047    0.000 /Users/username/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/reader.py:87(peek)
       53    0.038    0.001    0.038    0.001 <frozen importlib._bootstrap_external>:1053(open_resource)
   114364    0.030    0.000    0.054    0.000 /Users/username/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/scanner.py:145(need_more_tokens)
    13605    0.028    0.000    0.028    0.000 /Users/username/venvs/AaC/python/src/aac/lang/language_context.py:305(<listcomp>)
    22005    0.027    0.000    0.074    0.000 /Users/username/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/scanner.py:1311(scan_plain_spaces)
     8986    0.026    0.000    0.054    0.000 /opt/homebrew/Cellar/python@3.9/3.9.14/Frameworks/Python.framework/Versions/3.9/lib/python3.9/logging/__init__.py:282(__init__)


Wrote system design document to ../../../temp/alarm_clock_system_design_document.md
```

> *The above example is the top ten result from sorting based on the time taken from the code being run in `gen_design_doc_impl.py`
> With the above example output you can see that the code that this was run against has some hints of recursion occurring. 
> Without recursion occuring the two numbers at the top would be the same.*

Also to note from the output above you can see where some of the code that is being run multiple times and is taking up more time than others. It is recommended to see the full output at least first to make sure that eveyrthing is getting hit and run. Then, as you go, whittle down to find the code that is offending more often.

## Profile Description

`profile` is another deterministic profiler. There are a lot of similaarities to the `cProfile` however, this profiler has a significant amount of overhead and this profiler is pure python based. Therefore if you are needing to extend the profiler this can be done with this package.

It is recommended to use `cProfile` since it can cover the majority of use-cases, `profile` is when there is more overhead needed and the extra extensibility can be utiliized. You can find the `cProfile` documentation here: [cProfile Setup and Justification](./cprofile.md)

>*_NOTE: This profiler is a more advanced version of `cProfile` and has more extensibility and overhead that can be utilized. Majority of cases can be achieved with the `cProfile` package. 

### Getting Started with Profile

To get started using the `profile` package you will need to import this into the plugin that is being developed, new or existing.

To do so just use the import statement to bring it in:

```python
import profile
```

To enable the `profile` package is a little more complicated than the `cProfile` conterpart.
`profile` does not support using a Context Manager so the wrapping around the activity will be a little more work:

```python

""" Run Command for profile to run an AaC command within the plugin code """
profile.run(command, filename=None, sort=- 1)

""" This command is similar to run() except that it accepts globals and locals definitions that are supplied and passed through the command being executed. """
profile.runctx(command, globals, locals, filename=None, sort=- 1)

""" The Profile() class. This is really only needed for more precise controls over the profiling being done
than what the cProfile.run() method can provide. """
class profile.Profile(timer=None, timeunit=0.0, subcalls=True, builtins=True)
