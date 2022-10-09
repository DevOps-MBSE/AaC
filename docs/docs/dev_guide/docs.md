---
layout: default
title: Developing Docs
parent: Developer's Guide to AaC
nav_order: 2
---

# AaC Documentation
AaC documentation consists of two groups of generated documents: these jekyll pages and Sphinx API documentation for the Python API.

## Jekyll Docs
Jekyll docs are manually-maintained readme pages. We use these Jekyll docs to document topics such as user-facing documentation and developer-facing documentation (like this page).

### Setup
The Jekyll docs use the Ruby build tool [Bundler](https://bundler.io/). You'll need to have this installed in your local development environment.

If you haven't built the Jekyll docs before, you'll need to run `bundle install` inside the top-level repository directory `docs`. Voila! The links work, and you can create a public link to share with others to see.
### Starting the Preview Server


### Serving Jekyll Pages in Gitpod
Because Gitpod is a container-based development environment, it present some peculiarities for users who may be trying to server Jekyll files. One of the larger issues is that the Jekyll docs are using localhost or `0.0.0.0` as the base URL while the actual hostname is the Gitpod container's public address.

In order to override the localhost or `0.0.0.0` hostname when serving these pages, you'll need to set the environment variable `JEKYLL_ENV` to `production` like so:

`export JEKYLL_ENV=production`

Once Jekyll is in production mode, you'll need to override the `url` config value in `_config.yml` to be `https://4000-<gitpod instance URL>` (e.g. `https://4000-jondavidblack-aac-70of4eyyt7j.ws-us70.gitpod.io`)

Then just serve the pages `bundle exec jekyll s`

## Sphinx API Documentation
We use the automated documentation generation tool, [Sphinx](https://www.sphinx-doc.org/en/master/), for generating API documentation for the AaC Python package.

### Writing API Documentation

Regarding documentation, some guidelines for this project are as follows:

1. Write meaningful docstrings for all public API (i.e. public classes, functions, etc.);
   - Private functions are distinguished by the preceding `_` so, where a public function would be written `public_function`; a private function would be written as `_private_function`.
1. Write docstrings using the [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings);
1. Spelling matters, as much as possible, make sure your docstrings don't have things misspelled.

### Building the API Documentation

To generate the Sphinx API documentation, run:

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
