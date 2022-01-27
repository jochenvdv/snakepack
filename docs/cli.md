# CLI reference

Below is an overview of all possible arguments and options of the Snakepack CLI program.

## Help

You can display a short summary of Snakepack's arguments and options as a quick reference:

```shell
snakepack --help
```

## Base directory

The base directory is the directory in which Snakepack will be run. All paths in the configuration file will be relative to the base directory of your project.

### Default

By default, Snakepack uses the current working directory where you execute the command:

```shell
snakepack

# equivalent to
snakepack .

# or
snakepack $(pwd)
```

### Specifying another base directory

When you want to run Snakepack in another directory, you can pass this directory's path as an argument:

```shell
snakepack /path/to/my/base/dir
```

## Configuration file

In the configuration file all instructions for Snakepack's compiler are defined.

### Default

By default, Snakepack looks for a configuration file named ``snakepack.yml`` in the base directory:

````shell
snakepack

# equivalent to
snakepack --config-file ./snakepack.yml
````

### Specifying another configuration file

You can specify another name or location for the configuration file:

````shell
snakepack --config-file ../parent-folder/snakepack_config.yaml
````

## Running on multiple CPU cores

You can pass a flag to let Snakepack compile certain assets in parallel:

````shell
snakepack --parallel
snakepack -p # shorthand
````

## Logging output

You can control the verbosity of logging output:

````shell
snakepack --verbose # more detailed logging
snakepack -v # shorthand

# passing the flag twice produces even more verbose output
snakepack -vv
````
