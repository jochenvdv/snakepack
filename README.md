# Snakepack

Snakepack is a code bundler and minifier for Python.

## Getting started

### Installation

Snakepack is available on [PyPI](https://pypi.org/project/snakepack/).

Installing with [Pip](https://pypi.org/project/pip/):

```shell
pip install snakepack
```

Alternatively, you can use [Poetry](https://python-poetry.org/):

````shell
poetry install snakepack
````

### Usage

You can run Snakepack from the command line:

````shell
snakepack
````

Refer to the Quickstart in the documentation for further instructions on how to setup Snakepack for your project.

## Development

Contributing to Snakepack requires [Poetry](https://python-poetry.org/) to install dependencies. On MacOS, you can use [Homebrew](https://brew.sh/):

```shell
brew install poetry
```

Installing Snakepack's dependencies:

```shell
poetry install
```

Running the entire test suite against multiple Python versions requires Python 3.8 and Python 3.9, you can use [PyEnv](https://github.com/pyenv/pyenv) to install these:

```shell
brew install pyenv

pyenv install 3.8.12
pyenv install 3.9.9

# Run following commands within the project's directory
pyenv local 3.8.12
pyenv local 3.9.9
```

You'll also have to initialize the Git submodules to pull in the open source libraries we test against:

````shell
git submodule update --init
````

### Running the test suite

Running the unit tests:

```shell
pytest -k "not IntegrationTest and not AcceptanceTest"
```

Running the integration tests:

```shell
pytest -k "IntegrationTest" -m "not hypothesis"
```

Running the acceptance tests (takes a while):

```shell
pytest -n auto -k "AcceptanceTest
```

Running the entire test suite against multiple Python versions (takes a while):

```shell
tox
```