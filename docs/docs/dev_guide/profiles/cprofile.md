---
layout: default
title: cProfile Setup and Justification
parent: Developer's Guide to AaC
nav_order: 2
---

# cProfile Setup and Justification

## cProfile Description

`cProfile`, like `profile` is a deterministic profiler. Unlike the Python-backed `Profile`, `cProfile` is backed by the `lsprof` , and is a `C` extension.
This profiler is the one that comes recommended for most use-cases as it has reasonable overhead and works really well for some long running programs.

## Getting Started

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

with cProfile.Profile() as pr:
     with plugin_result(plugin_name, write_design_doc_to_directory) as result:
          s = io,StringIO() // this is used to capture any IO streams
          ps = pstats.Stats(pr, stream=s).sort_stats(SortKey.TIME)
          ps.print_stats(10)
          return result
```

```python
""" This is with using the `cProfile` profiler without the ContextManager Object """
import cProfile
import pstats
from pstats import SortKey

pr = cProfile.Profile()
pr.enable()
with plugin_result(plugin_name, write_design_doc_to_directory) as result:
     s = io.StringIO() // this is used to capture any IO streams
     sortby = SortKey.CUMULATIVE
     ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
     ps.print_stats()
     return result
```

So lets break this down a bit:
When you don't sort your results you can get a lot of noise from some functions and methods that are being called and can really
disorient and add to the confusion of what is going on with the plugin. The above code was run for the `gen_design_doc_impl.py` file
and within the results as seen with `ps.print_stats(10)` we are filtering the top ten from the line before its sort.

Through the sort function, and filtering the sort you can see the heavy offenders of the plugin that is being profiled.

The output from this run will have something similar to the below:

```bash
aac gen-design-doc ./model/alarm_clock/alarm_clock.yaml ../../../temp/
         4040225 function calls (3966008 primitive calls) in 1.194 seconds

   Ordered by: internal time
   List reduced from 1186 to 10 due to restriction <10>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    19692    0.085    0.000    0.085    0.000 /Users/charles.blackard/venvs/AaC/python/src/aac/lang/language_context.py:361(<listcomp>)
   107541    0.080    0.000    0.083    0.000 /Users/charles.blackard/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/reader.py:99(forward)
     8986    0.062    0.000    0.062    0.000 {method 'flush' of '_io.TextIOWrapper' objects}
     8489    0.054    0.000    0.219    0.000 /Users/charles.blackard/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/scanner.py:1270(scan_plain)
   452287    0.047    0.000    0.047    0.000 /Users/charles.blackard/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/reader.py:87(peek)
       53    0.038    0.001    0.038    0.001 <frozen importlib._bootstrap_external>:1053(open_resource)
   114364    0.030    0.000    0.054    0.000 /Users/charles.blackard/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/scanner.py:145(need_more_tokens)
    13605    0.028    0.000    0.028    0.000 /Users/charles.blackard/venvs/AaC/python/src/aac/lang/language_context.py:305(<listcomp>)
    22005    0.027    0.000    0.074    0.000 /Users/charles.blackard/venvs/AaC/python/venv/lib/python3.9/site-packages/yaml/scanner.py:1311(scan_plain_spaces)
     8986    0.026    0.000    0.054    0.000 /opt/homebrew/Cellar/python@3.9/3.9.14/Frameworks/Python.framework/Versions/3.9/lib/python3.9/logging/__init__.py:282(__init__)


Wrote system design document to ../../../temp/alarm_clock_system_design_document.md
```

> *The above example is the top ten result from sorting based on the time taken from the code being run in `gen_design_doc_impl.py`
> With the above example output you can see that the code that this was run against has some hints of recursion occurring. 
> Without recursion occuring the two numbers at the top would be the same.*
