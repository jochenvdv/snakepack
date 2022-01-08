import logging
import sys
from logging import getLogger, StreamHandler
from pathlib import Path

import click

from snakepack.bundlers.generic import FileBundler
from snakepack.compiler import Compiler, SynchronousExecutor, ConcurrentExecutor
from snakepack.config._base import register_components
from snakepack.config.formats import parse_yaml_config
from snakepack.loaders.python import ImportGraphLoader
from snakepack.packagers.generic import DirectoryPackager
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer

DEFAULT_CONFIG_FILE = 'snakepack.yml'

register_components()


@click.command()
@click.argument('base_dir', required=False, default=Path('.').resolve(), type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('-c', '--config-file', required=False, type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option('-p', '--parallel', required=False, default=False, is_flag=True)
@click.option('-v', '--verbose', required=False, count=True)
def snakepack(base_dir, config_file=None, parallel=False, verbose=0):
    if config_file is None:
        config_file = Path(base_dir) / DEFAULT_CONFIG_FILE

    with open(config_file) as f:
        config_yaml = f.read()

    config = parse_yaml_config(config_yaml)
    logger = _create_logger(verbose)
    sync_executor = SynchronousExecutor(logger=logger)

    if parallel:
        executor = ConcurrentExecutor(logger=logger, sync_executor=sync_executor)
    else:
        executor = sync_executor

    compiler = Compiler(config=config, executor=executor)
    compiler.run()


def _create_logger(verbosity):
    stdout_handler = StreamHandler(sys.stdout)

    if verbosity == 0:
        stdout_handler.setLevel(logging.WARN)
    elif verbosity == 1:
        stdout_handler.setLevel(logging.INFO)
    elif verbosity >= 2:
        stdout_handler.setLevel(logging.DEBUG)

    logger = getLogger('snakepack')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    return logger
