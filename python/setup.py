import logging
from setuptools import find_packages, setup
from src.aac import __version__

README_FILE_PATH = "../README.md"

try:
    with open(README_FILE_PATH, "r") as file_handler:
        readme_description = file_handler.read()
except Exception as exception:
    logging.error(f"Failed to open readme file {README_FILE_PATH} with error:\n {exception}")
    readme_description = ""

runtime_dependencies = [
    "attrs ~= 22.2.0",
    "pyrsistent ~= 0.19.3",
    "PyYAML ~= 6.0.0",
    "types-PyYAML ~= 6.0.12.2",
    "six ~= 1.16.0",
    "click ~= 8.1.3",
    "pathspec ~= 0.10.3",
    "regex ~= 2022.10.31",
    "typing-extensions ~= 4.4.0",
    "pluggy ~= 1.0.0",
    "Jinja2 ~= 3.1.2",
    "MarkupSafe ~= 2.1.1",
    "pygls ~= 0.13.1",
    "fastapi ~= 0.89.0",
    "starlette >= 0.22.0",
    "anyio < 5, ~= 3.6.2",
    "sniffio ~= 1.3.0",
    "uvicorn ~= 0.20.0",
    "requests >= 2.28.1",
]

development_dependencies = [
    "wheel ~= 0.41.0",
    "pip-tools >= 6.9.0",
    "tomli < 2.0.0",
    "black >= 22.3.0",
    "platformdirs >= 2.4",
    "coverage >= 6.0",
    "mccabe >= 0.6.1",
    "mypy ~= 1.1.0",
    "mypy-extensions ~= 1.0.0",
    "pycodestyle >= 2.8.0",
    "pyflakes >= 2.4",
    "build == 0.7.0",
    "twine == 3.4.2",
    "pipdeptree >= 2.2.0",
    "Pygments >= 2.5.1",
    "types-PyYAML >= 6.0.9",
    "requests >= 2.27.0",
]

documentation_dependencies = [
    "sphinx ~= 6.1.3",
    "sphinxcontrib-applehelp ~= 1.0.2",
    "sphinxcontrib-devhelp ~= 1.0.2",
    "sphinxcontrib-htmlhelp ~= 2.0.0",
    "sphinxcontrib-jsmath ~= 1.0.1",
    "sphinxcontrib-qthelp ~= 1.0.3",
    "sphinxcontrib-serializinghtml ~= 1.1.9",
    "sphinx-copybutton ~= 0.5.2",
    "sphinx_contributors ~= 0.2.7",
    "sphinx-autobuild ~= 2021.3.14",
    "furo ~= 2023.7.26",
    "docutils ~= 0.19",
    "myst-parser ~= 2.0.0",
    "pytz ~= 2023.3"
]

test_dependencies = [
    "tox >= 3.24",
    "nose2 >= 0.10.0",
    "coverage >= 6.0",
    "flake8 >= 4.0",
    "flake8-docstrings >= 1.6.0",
    "flake8-fixme >= 1.1.1",
    "flake8-eradicate >= 1.5.0",
    "flake8-assertive >= 1.3.0",
    "eradicate<3.0,>=2.0",
    "httpx >= 0.23.0",
]

setup(
    name="aac",
    version=__version__,
    description=(
        "A distinctly different take on Model-Based System Engineering (MBSE) that allows a system modeller to define a system in simple yaml. "
    ),
    license="",
    long_description=readme_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src", exclude="tests"),
    package_dir={"": "src"},
    package_data={"": ["*.aac", "*.jinja2", "*.yaml"]},
    install_requires=runtime_dependencies,
    setup_requires=development_dependencies,
    tests_require=test_dependencies,
    entry_points={
        "console_scripts": [
            "aac=aac.execute.command_line:cli",
        ]
    },
    extras_require={
        "test": test_dependencies,
        "dev": development_dependencies,
        "docs": documentation_dependencies,
        "all": test_dependencies + development_dependencies + documentation_dependencies,
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    keywords=["MBSE"],
)
