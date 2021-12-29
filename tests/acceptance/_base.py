import importlib
import shutil
import subprocess
import sys
from abc import abstractmethod
from pathlib import Path
from uuid import uuid4

import pytest

from snakepack.config.formats import generate_yaml_config
from snakepack.config.model import SnakepackConfig, PackageConfig, BundleConfig
from snakepack.config.options import ComponentConfig
from snakepack.config.types import FullyQualifiedPythonName
from snakepack.loaders.python import ImportGraphLoader, PackageLoader
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
        loader_config = ComponentConfig(
            name='import_graph',
            options=ImportGraphLoader.Options(
                entry_point=self._APPLICATION_ENTRY_POINT
            )
        )
        config = self._create_config(test_path, loader_config, transformer, roundtrip)

        return config

    def _create_library_config(self, test_path, transformer=None, roundtrip=False):
        loader_config = ComponentConfig(
            name='package',
            options=PackageLoader.Options(
                pkg_name=FullyQualifiedPythonName('snakepack')
            )
        )
        config = self._create_config(test_path, loader_config, transformer, roundtrip)

        return config

    def _create_config(self, test_path, loader_config, transformer, roundtrip):
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
                            loader=loader_config,
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
        if roundtrip:
            main_module = config.source_base_path / 'snakepack/__main__.py'
            main_module_code = main_module.read_text()
            main_module_code = f"import sys; sys.path.insert(0, '{config.source_base_path}')\n" + main_module_code
            main_module.write_text(main_module_code)

            try:
                result = subprocess.check_output(
                    args=f"PYTHONPATH={config.source_base_path}:$PYTHONPATH python {config.source_base_path / 'snakepack/__main__.py'} --config-file={config_path}",
                    shell=True,
                    stderr=subprocess.STDOUT
                )
                print('ok:' + result.decode('utf-8'))
            except subprocess.CalledProcessError as e:
                print(e.output)
                pytest.fail('Snakepack round-trip invocation failed')
        else:
            import snakepack.app
            result = cli_runner.invoke(snakepack.app.snakepack, [f'--config-file={config_path}'])
            print(result.output)

            assert result.exit_code == 0, 'Snakepack invocation failed'

        # test compilation of output files
        failed_compilations = []

        for file in config.target_base_path.iterdir():
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

    def _report_after_metrics(self, test_name, directory):
        pass

    def _report_metrics(self, test_name, metrics):
        pass

    def _measure_metrics(self, directory):
        pass

    @abstractmethod
    def _test_compiled_output(self, dist_path: Path):
        raise NotImplemented