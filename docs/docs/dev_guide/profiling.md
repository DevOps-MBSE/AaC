---
layout: default
title: Profiling AaC and Plugins
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

```shell

$ aac gen-design-doc ./model/alarm_clock/alarm_clock.yaml ../../../temp/
         4040214 function calls (3965997 primitive calls) in 1.129 seconds

   Ordered by: cumulative time
   List reduced from 1186 to 10 due to restriction <10>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     58/1    0.000    0.000    1.130    1.130 /opt/homebrew/Cellar/python@3.9/3.9.14/Frameworks/Python.framework/Versions/3.9/lib/python3.9/contextlib.py:114(__enter__)
   2732/2    0.000    0.000    1.130    0.565 {built-in method builtins.next}
        2    0.000    0.000    1.130    0.565 /Users/charles.blackard/venvs/AaC/python/src/aac/plugins/plugin_execution.py:59(plugin_result)
        1    0.000    0.000    1.130    1.130 /Users/charles.blackard/venvs/AaC/python/src/aac/plugins/first_party/gen_design_doc/gen_design_doc_impl.py:35(write_design_doc_to_directory)
        1    0.000    0.000    1.095    1.095 /Users/charles.blackard/venvs/AaC/python/src/aac/plugins/first_party/gen_design_doc/gen_design_doc_impl.py:59(_get_parsed_models)
        2    0.000    0.000    1.095    0.547 /Users/charles.blackard/venvs/AaC/python/src/aac/validate/_validate.py:54(validated_source)
        1    0.000    0.000    1.056    1.056 /Users/charles.blackard/venvs/AaC/python/src/aac/validate/_validate.py:68(_with_validation)
        1    0.000    0.000    1.056    1.056 /Users/charles.blackard/venvs/AaC/python/src/aac/validate/_validate.py:80(_validate_definitions)
       83    0.000    0.000    0.589    0.007 /Users/charles.blackard/venvs/AaC/python/src/aac/lang/active_context_lifecycle_manager.py:10(get_active_context)
        1    0.000    0.000    0.589    0.589 /Users/charles.blackard/venvs/AaC/python/src/aac/lang/active_context_lifecycle_manager.py:29(get_initialized_language_context)

Wrote system design document to ../../../temp/alarm_clock_system_design_document.md

Wrote system design document to temp/alarm_clock_system_design_document.md
```

> *The above example is the top ten result from sorting based on the time taken from the code being run in `gen_design_doc_impl.py`
> With the above example output you can see that the code that this was run against has some hints of recursion occurring.
> Without recursion occuring the two numbers at the top would be the same.*
> Also to note: You can see the code that was run and the ten highest length of time the code was being run. With `ncalls` you can see how many times the code was being hit and ran against.

Also to note from the output above you can see where some of the code that is being run multiple times and is taking up more time than others. It is recommended to see the full output at least first to make sure that eveyrthing is getting hit and run. Then, as you go, whittle down to find the code that is offending more often.

## Profile Description

`profile` is another deterministic profiler. There are a lot of similarities to the `cProfile` however, this profiler has a significant amount of overhead and this profiler is pure python based. Therefore, if you need to extend the profiler, you can accomplish that with this package.

It is recommended to use `cProfile` for the majority of use-cases, and to use `profile` for extensibility and when there is less consideration for overhead or performance.

>*_NOTE*_: This profiler is a more advanced version of `cProfile` and has more extensibility and overhead that can be utilized. Majority of cases can be achieved with the `cProfile` package.

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
```
