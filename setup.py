from setuptools import setup, find_packages

runtime_dependencies = [
    'attrs == 21.2.0',
    'coverage == 6.0',
    'jsonschema == 4.0.1',
    'pyrsistent == 0.18.0',
    'PyYAML == 5.4.1',
    'six == 1.16.0',
]

development_dependencies = [
    'flake8'
]

test_dependencies = [
    'nose2 == 0.10.0'
]

setup(
    name = 'Jellyfish',
    version = '3.0.0',
    packages = find_packages(where="app/src"),
    package_dir = {"": "app/src"},
    install_requires = runtime_dependencies,
    setup_requires = development_dependencies,
    tests_require = test_dependencies,
    extras_require = {
        'test' : test_dependencies,
        'dev' : development_dependencies,
        'all' : test_dependencies + development_dependencies
    }
)
