# Quickstart

Following this guide will get you working with Snakepack in your project in no time.

### Installation

Ideally, install Snakepack as a development dependency in your project:

```shell
poetry add --dev snakepack
```

### Configuration

Before we can run Snakepack, we need to create a configuration file. The default configuration file location is `{PROJECT_ROOT}/snakepack.yml`:

```shell
touch snakepack.yml
```

Then, using your editor of choice, add the following contents:

````yaml
packages:
  snakepack:
    packager:
      # The directory packager will output the whole package in a directory
      name: directory
    bundles:
      snakepack:
        bundler:
          # The file bundler will output normal Python files 1-to-1
          # from an input file (after transformation)
          name: file
        loader:
          # You can specify the import graph loader to detect & load all imported files
          # in your Python application
          name: import_graph
          options:
            # This is the entry point module of your application
            entry_point: 'your_source_dir/entry_point.py'
        transformers:
          # You can add/remove transformers as needed here
          - name: remove_comments
          - name: remove_assertions
          - name: remove_whitespace
          - name: remove_semicolons
          - name: remove_pass
          - name: remove_object_base
          - name: remove_parameter_separators
          - name: remove_literal_statements
          - name: remove_annotations
          - name: hoist_literals
            options:
              # You can configure options for each transformer
              excludes:
                # Every transformer supports the option 'excludes' by default
                - 'your_source_dir/some_module'
          - name: rename_identifiers

````

Refer to the [Configuration documentation](config.md) for more details on the configuration file.

### Running Snakepack

Once you have a configuration file, running Snakepack is as simple as:

````shell
snakepack
````

Refer to the [CLI reference documentation](cli.md) for more details on the command line program of Snakepack.