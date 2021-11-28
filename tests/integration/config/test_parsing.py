from pathlib import Path
from textwrap import dedent

import pytest

from snakepack.bundlers.generic import FileBundler
from snakepack.config import ConfigException
from snakepack.config.options import ComponentConfig
from snakepack.config.model import SnakepackConfig, PackageConfig, BundleConfig
from snakepack.config.parsing import parse_yaml_config
from snakepack.loaders.python import ImportGraphLoader
from snakepack.packagers.generic import DirectoryPackager
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer


class ParseYamlConfigIntegrationTest:
    def test_full(self):
        yaml = dedent(
            """
            source_base_path: 'src/'
            target_base_path: 'dist/'
            
            packages:
              snakepack:
                packager:
                  name: directory
                  options:
                    output_path: 'snakepack_pkg/'
                bundles:
                  snakepack:
                    bundler:
                      name: file
                      options:
                    loader:                   
                      name: import_graph
                      options:
                        entry_point: 'snakepack.py'
                    transformers:
                        - name: remove_comments
                          options:
            """
        )

        parsed_config = parse_yaml_config(yaml)

        assert parsed_config == SnakepackConfig(
            source_base_path=Path('src/'),
            target_base_path=Path('dist/'),
            packages={
                'snakepack': PackageConfig(
                    packager=ComponentConfig(
                        name='directory',
                        options=DirectoryPackager.Options(
                            output_path='snakepack_pkg/'
                        )
                    ),
                    bundles={
                        'snakepack': BundleConfig(
                            bundler=ComponentConfig(
                                name='file',
                                options=FileBundler.Options()
                            ),
                            loader=ComponentConfig(
                                name='import_graph',
                                options=ImportGraphLoader.Options(
                                    entry_point=Path('snakepack.py')
                                )
                            ),
                            transformers=[
                                ComponentConfig(
                                    name='remove_comments',
                                    options=RemoveCommentsTransformer.Options()
                                )
                            ]
                        )
                    }
                )
            }
        )

    def test_invalid_yaml(self):
        yaml = dedent(
            """
            packages:
                :
            """
        )

        with pytest.raises(ConfigException):
            parse_yaml_config(yaml)