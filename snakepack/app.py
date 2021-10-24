from pathlib import Path

import click

from snakepack.bundlers.generic import FileBundler
from snakepack.compiler import Compiler
from snakepack.config._base import register_components
from snakepack.config.parsing import parse_yaml_config
from snakepack.loaders.python import ImportGraphLoader
from snakepack.packagers.generic import DirectoryPackager
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer

DEFAULT_CONFIG_FILE = 'snakepack.yml'

register_components()


@click.command()
@click.argument('base_dir', required=False, type=click.Path(exists=True, file_okay=False, resolve_path=True))
def snakepack(base_dir):
    if base_dir is None:
        config_file = Path('.') / DEFAULT_CONFIG_FILE
    else:
        config_file = Path(base_dir) / DEFAULT_CONFIG_FILE

    with open(config_file) as f:
        config_yaml = f.read()

    config = parse_yaml_config(config_yaml)
    compiler = Compiler(config=config)
    compiler.run()
