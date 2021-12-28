import shutil
from pathlib import Path

import pytest

from snakepack.app import snakepack
from snakepack.config.formats import generate_yaml_config
from snakepack.config.model import SnakepackConfig, PackageConfig, BundleConfig
from snakepack.config.options import ComponentConfig
from snakepack.loaders.python import ImportGraphLoader
from snakepack.packagers.generic import DirectoryPackager
from snakepack.transformers.python import __all__ as all_transformers

_ALL_TRANSFORMERS = [transformer.__config_name__ for transformer in all_transformers]


def per_transformer():
    return pytest.mark.parametrize('transformer', _ALL_TRANSFORMERS)


class BaseAcceptanceTest:
    _SUBJECT_NAME = NotImplemented
    _SOURCEDIR = NotImplemented
    _APPLICATION_ENTRY_POINT = NotImplemented
    _LIBRARY_PACKAGE = NotImplemented

    def _create_application_config(self, tmp_path, transformer=None):
        if transformer is None:
            transformers = _ALL_TRANSFORMERS
        else:
            transformers = [transformer]

        config = SnakepackConfig(
            source_base_path=self._SOURCEDIR,
            target_base_path=tmp_path / 'dist',
            packages={
                self._SUBJECT_NAME: PackageConfig(
                    packager=ComponentConfig(name='directory'),
                    bundles={
                        self._SUBJECT_NAME: BundleConfig(
                            bundler=ComponentConfig(name='file'),
                            loader=ComponentConfig(
                                name='import_graph',
                                options=ImportGraphLoader.Options(
                                    entry_point=self._SOURCEDIR / self._APPLICATION_ENTRY_POINT
                                )
                            ),
                            transformers=[
                                ComponentConfig(name=transformer_name)
                                for transformer_name in transformers
                            ]
                        )
                    }
                )
            }
        )

        return config

    def _create_library_config(self, transformer=None):
        config = SnakepackConfig()

        return config

    def _create_config(self, transformer):
        pass

    def _test_snakepack(self, cli_runner, tmp_path: Path, config: SnakepackConfig):
        # create test directory and config file
        shutil.rmtree(tmp_path)
        tmp_path.mkdir()
        config_path = tmp_path / 'config.yml'
        config_path.write_text(generate_yaml_config(config))

        # run Snakepack
        result = cli_runner.invoke(snakepack, [f'--config-file={config_path}'])

        # test outcome
        assert result.exit_code == 0, f'Snakepack invocation failed with output:\n\n{result.output}'

    def _report_after_metrics(self, test_name, directory):
        pass

    def _report_metrics(self, test_name, metrics):
        pass

    def _measure_metrics(self, directory):
        pass