from pathlib import Path

import click

from snakepack.bundlers.generic import FileBundler
from snakepack.compiler import Compiler, SynchronousExecutor, ConcurrentExecutor
from snakepack.config._base import register_components
from snakepack.config.parsing import parse_yaml_config
from snakepack.loaders.python import ImportGraphLoader
from snakepack.packagers.generic import DirectoryPackager
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer

DEFAULT_CONFIG_FILE = 'snakepack.yml'

register_components()


@click.command()
@click.argument('base_dir', required=False, default=Path('.').resolve(), type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('-c', '--config-file', required=False, type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option('-p', '--parallel', required=False, default=False, is_flag=True)
def snakepack(base_dir, config_file=None, parallel=False):
    if config_file is None:
        config_file = Path(base_dir) / DEFAULT_CONFIG_FILE

    with open(config_file) as f:
        config_yaml = f.read()

    config = parse_yaml_config(config_yaml)

    if parallel:
        executor = ConcurrentExecutor(sync_executor=SynchronousExecutor())
    else:
        executor = SynchronousExecutor()

    compiler = Compiler(config=config, executor=executor)
    compiler.run()
