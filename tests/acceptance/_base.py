import importlib
import pkgutil
import shutil
import subprocess
import sys
from abc import abstractmethod
from pathlib import Path
from typing import Tuple, Iterable
from uuid import uuid4

import pytest
from boltons.iterutils import first

from snakepack.config.formats import generate_yaml_config
from snakepack.config.model import SnakepackConfig, PackageConfig, BundleConfig
from snakepack.config.options import ComponentConfig
from snakepack.config.types import FullyQualifiedPythonName
from snakepack.loaders.python import ImportGraphLoader, PackageLoader
from snakepack.packagers.generic import DirectoryPackager
from snakepack.transformers.python import __all__ as all_transformers
from snakepack.transformers.python import RenameIdentifiersTransformer

ALL_TRANSFORMERS = [transformer.__config_name__ for transformer in all_transformers]


def per_transformer():
    return pytest.mark.parametrize('transformer', ALL_TRANSFORMERS)


class BaseAcceptanceTest:
    _SUBJECT_NAME = NotImplemented
    _SOURCEDIR = NotImplemented
    _APPLICATION_ENTRY_POINT = NotImplemented
    _EXTRA_INCLUDES = NotImplemented
    _LIBRARY_PACKAGES = NotImplemented
    _PKG_BASE_PATH = None
    _TEST_CMD = NotImplemented
    _EXTRA_TEST_FILES = NotImplemented
    _PRETEST_CMD = NotImplemented

    def _create_application_config(self, test_path, transformers=None, roundtrip=False):
        if transformers is None:
            transformers = []

        loader_config = ComponentConfig(
            name='import_graph',
            options=ImportGraphLoader.Options(
                entry_point=self._APPLICATION_ENTRY_POINT,
                includes=self._EXTRA_INCLUDES
            )
        )
        bundles = {
            self._SUBJECT_NAME: BundleConfig(
                bundler=ComponentConfig(name='file'),
                loader=loader_config,
                transformers=[
                    self._create_transformer_config(transformer_name)
                    for transformer_name in transformers
                ]
            )
        }
        config = self._create_config(test_path, bundles, transformers, roundtrip)

        return config

    def _create_library_config(self, test_path, transformers=None, roundtrip=False):
        if transformers is None:
            transformers = []

        bundles = {
            library_pkg: BundleConfig(
                bundler=ComponentConfig(name='file'),
                loader=ComponentConfig(
                    name='package',
                    options=PackageLoader.Options(
                        pkg_name=FullyQualifiedPythonName(library_pkg),
                        pkg_base_path=self._PKG_BASE_PATH
                    )
                ),
                transformers=[
                    self._create_transformer_config(transformer_name)
                    for transformer_name in transformers
                ]
            )
            for library_pkg in self._LIBRARY_PACKAGES
        }

        config = self._create_config(test_path, bundles, transformers, roundtrip)

        return config

    def _create_config(self, test_path, bundles, transformers, roundtrip):
        if transformers is None:
            transformers = []

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
                    bundles=bundles
                )
            }
        )

        return config

    def _create_test_path(self, tmp_path):
        test_path = tmp_path / str(uuid4())
        test_path.mkdir(parents=True)

        return test_path

    def _test_snakepack(self, cli_runner, test_path: Path, config: SnakepackConfig, roundtrip=False, results_bag=None):
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
                print(result.decode('utf-8'))
            except subprocess.CalledProcessError as e:
                print(e.output.decode('utf-8'))
                pytest.fail('Snakepack round-trip invocation failed')
        else:
            import snakepack.app
            result = cli_runner.invoke(snakepack.app.snakepack, [f'--config-file={config_path}'])
            print(result.output)
            assert result.exit_code == 0, 'Snakepack invocation failed'

        # test compilation of output files
        failed_compilations = self._check_dir_compilation(config.target_base_path)

        if len(failed_compilations) > 0:
            if roundtrip:
                failure_msg = f"Failed to compile output files:\n\n{failed_compilations}\n'"
            else:
                failure_msg = f"Failed to compile round-trip output files:\n\n'{failed_compilations}\n'"

            pytest.fail(failure_msg)

        # collect metrics
        if results_bag is not None:
            num_files, total_size_in_bytes = self._collect_metrics_for_dir(config.target_base_path, config)
            results_bag.num_files = num_files
            results_bag.total_size_in_bytes = total_size_in_bytes

    @staticmethod
    def _check_dir_compilation(path: Path) -> Iterable[Path]:
        failed_compilations = []

        for sub_path in path.iterdir():
            if sub_path.is_file() and sub_path.name.endswith('.py'):
                file_content = sub_path.read_text()

                try:
                    compile(
                        source=file_content,
                        filename=str(sub_path),
                        mode='exec'
                    )
                except SyntaxError as e:
                    print("Failed: " + sub_path, file_content)
                    failed_compilations.append(sub_path)
            elif sub_path.is_dir():
                failed_compilations.extend(BaseAcceptanceTest._check_dir_compilation(sub_path))

        return failed_compilations

    @staticmethod
    def _collect_metrics_for_dir(path: Path, config) -> Tuple[int, int]:
        num_files = 0
        total_size_in_bytes = 0

        for sub_path in path.iterdir():
            if sub_path.is_dir():
                dir_num_files, dir_total_size_in_bytes = BaseAcceptanceTest._collect_metrics_for_dir(sub_path, config)
                num_files += dir_num_files
                total_size_in_bytes += dir_total_size_in_bytes
            elif sub_path.is_file():
                num_files += 1
                total_size_in_bytes += sub_path.stat().st_size

        return num_files, total_size_in_bytes

    def _create_transformer_config(self, transformer_name) -> ComponentConfig:
        if transformer_name == 'rename_identifiers':
            return ComponentConfig(
                name=transformer_name,
                options=RenameIdentifiersTransformer.Options(
                    excludes=[
                        'pkg_resources',
                        'loky',
                        'pydantic',
                        'libcst'
                    ]
                )
            )

        if transformer_name == 'remove_unreferenced_code':
            return ComponentConfig(
                name=transformer_name,
                options=RenameIdentifiersTransformer.Options(
                    excludes=[
                        'typing_extensions',
                        'pkg_resources'
                    ]
                )
            )

        transformer_class = first(filter(lambda x: x.__config_name__ == transformer_name, all_transformers))

        return ComponentConfig(
            name=transformer_name,
            options=transformer_class.Options(
                excludes=[
                    'pkg_resources'
                ]
            )
        )

    def _prepare_virtual_env(self, venv):
        pretest_cmd = self._PRETEST_CMD.format(venv_path=venv.bin)
        print(pretest_cmd)

        try:
            result = subprocess.check_output(
                args=pretest_cmd,
                shell=True,
                stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            print(e.output.decode('utf-8'))
            pytest.fail('Failed to execute pre-install command')

    def _test_library_compiled_output(self, test_path: Path, venv=None) -> bool:
        if venv is not None:
            self._prepare_virtual_env(venv)

        dist_path = test_path / 'dist-initial' / self._SUBJECT_NAME
        command = self._TEST_CMD.format(
            dist_path=str(dist_path),
            venv_path=venv.bin if venv else '.'
        )
        print(command)

        for extra_file in self._EXTRA_TEST_FILES:
            input_path = self._SOURCEDIR / extra_file
            output_path = test_path / 'dist-initial' / self._SUBJECT_NAME / extra_file
            content = input_path.read_text()
            output_path.write_text(content)

        try:
            result = subprocess.check_output(
                args=command,
                shell=True,
                stderr=subprocess.STDOUT,
            )
            print(result.decode('utf-8'))
            tests_pass = True
        except subprocess.CalledProcessError as e:
            print(e.output.decode('utf-8'))
            tests_pass = False

        assert tests_pass, 'Running test suite on compiled files fails'
