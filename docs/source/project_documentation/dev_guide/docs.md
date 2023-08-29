---
layout: default
title: Developing Docs
parent: Developer's Guide to AaC
nav_order: 2
---

# AaC Documentation
AaC documentation consists of two groups of generated documents: Sphinx project documentation and Sphinx API documentation for the Python API.

## Sphinx API Documentation
We use the automated documentation generation tool, [Sphinx](https://www.sphinx-doc.org/en/master/), for generating API documentation for the AaC Python package.

### Writing API Documentation
Regarding documentation, some guidelines for this project are as follows:

1. Write meaningful docstrings for all public API (i.e. public classes, functions, etc.);
   - Private functions are distinguished by the preceding `_` so, where a public function would be written `public_function`; a private function would be written as `_private_function`.
1. Write docstrings using the [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings);
1. Spelling matters, as much as possible, make sure your docstrings don't have things misspelled.

### Building the Sphinx Documentation
To generate the Sphinx documentation, run:

```bash
$ cd docs/
$ make html
```

Once you've run the above `make` command, you can view the documentation by opening the `build/html/index.html` file in a web browser, or by doing the following:

```bash
$ cd build/html/
$ python -m http.server 3000
```

After this, you can navigate to http://127.0.0.1:3000 to view the documentation.
