---
layout: default
title: Developing Docs
parent: dev_guide
nav_order: 2
---
### Documenting

#### Writing API Documentation

Regarding documentation, some guidelines for this project are as follows:

1. Write meaningful docstrings for all public API (i.e. public classes, functions, etc.);
   - Private functions are distinguished by the preceding `_` so, where a public function would be written `public_function`; a private function would be written as `_private_function`.
1. Write docstrings using the [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings);
1. Spelling matters, as much as possible, make sure your docstrings don't have things misspelled.

#### Generating API Documentation

To generate API documentation, run:

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
