import shutil
from abc import abstractmethod
from pathlib import Path
from uuid import uuid4

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

    def _create_application_config(self, test_path, transformer=None, roundtrip=False):
        if transformer is None:
            transformers = _ALL_TRANSFORMERS
        else:
            transformers = [transformer]

        if roundtrip:
            target_base_path = test_path / 'dist-roundtrip'
            source_base_path = test_path / 'dist-initial' / self._SUBJECT_NAME
        else:
            target_base_path = test_path / 'dist-initial'
            source_base_path = self._SOURCEDIR

        config = SnakepackConfig(
            source_base_path=source_base_path,
            target_base_path=target_base_path,
            packages={
                self._SUBJECT_NAME: PackageConfig(
                    packager=ComponentConfig(name='directory'),
                    bundles={
                        self._SUBJECT_NAME: BundleConfig(
                            bundler=ComponentConfig(name='file'),
                            loader=ComponentConfig(
                                name='import_graph',
                                options=ImportGraphLoader.Options(
                                    entry_point=self._APPLICATION_ENTRY_POINT
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

    def _create_library_config(self, test_path, transformer=None):
        config = SnakepackConfig()

        return config

    def _create_config(self, transformer):
        pass

    def _create_test_path(self, tmp_path):
        test_path = tmp_path / str(uuid4())
        test_path.mkdir(parents=True)

        return test_path

    def _test_snakepack(self, cli_runner, test_path: Path, config: SnakepackConfig, roundtrip=False):
        # create config file
        config_path = test_path / 'config.yml'
        print(generate_yaml_config(config))
        config_path.write_text(generate_yaml_config(config))

        # run Snakepack
        result = cli_runner.invoke(snakepack, [f'--config-file={config_path}'])
        print(result.output)

        # test CLI program
        failure_msg = 'Snakepack round-trip invocation failed' if roundtrip else 'Snakepack invocation failed'
        assert result.exit_code == 0, failure_msg

        # test compilation of output files
        if roundtrip:
            dist_path = test_path / 'dist-roundtrip'
        else:
            dist_path = test_path / 'dist-initial'
        failed_compilations = []

        for file in dist_path.iterdir():
            if file.is_file():
                file_content = file.read_text()

                try:
                    compile(
                        source=file_content,
                        filename=str(file),
                        mode='exec'
                    )
                except SyntaxError as e:
                    failed_compilations.append(file)

        if len(failed_compilations) > 0:
            if roundtrip:
                failure_msg = f"Failed to compile output files:\n\n- '{file}\n'"
            else:
                failure_msg = f"Failed to compile round-trip output files:\n\n- '{file}\n'"

            pytest.fail(failure_msg)

        return dist_path

    def _report_after_metrics(self, test_name, directory):
        pass

    def _report_metrics(self, test_name, metrics):
        pass

    def _measure_metrics(self, directory):
        pass

    @abstractmethod
    def _test_compiled_output(self, dist_path: Path):
        raise NotImplemented