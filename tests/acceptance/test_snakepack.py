from pathlib import Path

import pytest

from snakepack.app import snakepack
from tests.acceptance._base import BaseAcceptanceTest, per_transformer, ALL_TRANSFORMERS


class SnakepackAcceptanceTest(BaseAcceptanceTest):
    _SUBJECT_NAME = 'snakepack'
    _SOURCEDIR = Path(__file__).resolve().parent.parent.parent
    _APPLICATION_ENTRY_POINT = 'snakepack/__main__.py'
    _EXTRA_INCLUDES = ['pkg_resources._vendor.appdirs']
    _LIBRARY_PACKAGES = ['snakepack', 'tests']
    _TEST_CMD = 'pytest -m "not hypothesis" -k "not AcceptanceTest" {dist_path}/tests'
    _EXTRA_TEST_FILES = ['pyproject.toml']
    # application tests (import graph loader)

    def test_snakepack_as_application_with_no_transformers(self, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_application_config(transformers=None, test_path=test_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)
        self._test_application_compiled_output(test_path=test_path, cli_runner=cli_runner)

    def test_snakepack_as_application_with_all_transformers(self, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_application_config(transformers=ALL_TRANSFORMERS, test_path=test_path)

        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)
        self._test_application_compiled_output(test_path=test_path, cli_runner=cli_runner)

    @per_transformer()
    def test_snakepack_as_application_with_each_transformer_individually(self, transformer, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_application_config(transformers=[transformer], test_path=test_path)

        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)
        self._test_application_compiled_output(test_path=test_path, cli_runner=cli_runner)

    # library tests (package loader)

    def test_snakepack_as_library_with_no_transformers(self, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_library_config(transformers=None, test_path=test_path)

        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)
        self._test_library_compiled_output(test_path=test_path)

    def test_snakepack_as_library_with_all_transformers(self, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_library_config(transformers=ALL_TRANSFORMERS, test_path=test_path)

        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)
        self._test_library_compiled_output(test_path=test_path)

    @per_transformer()
    def test_snakepack_as_library_with_each_transformer_individually(self, transformer, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_library_config(transformers=[transformer], test_path=test_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)
        self._test_library_compiled_output(test_path=test_path)

    def _test_application_compiled_output(self, test_path, cli_runner):
        config = self._create_application_config(test_path=test_path, roundtrip=True)
        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, roundtrip=True)