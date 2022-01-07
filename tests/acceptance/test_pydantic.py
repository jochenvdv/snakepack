from pathlib import Path

import pytest

from snakepack.app import snakepack
from tests.acceptance._base import BaseAcceptanceTest, per_transformer, ALL_TRANSFORMERS


class PydanticAcceptanceTest(BaseAcceptanceTest):
    _SUBJECT_NAME = 'pydantic'
    _SOURCEDIR = Path(__file__).resolve().parent / 'subjects' / _SUBJECT_NAME
    _LIBRARY_PACKAGES = ['pydantic', 'tests']
    _PRETEST_CMD = f'{{venv_path}}/pip install -r {str(_SOURCEDIR)}/tests/requirements-testing.txt'
    _TEST_CMD = ' {venv_path}/pytest -p no:hypothesis-6.32.1 {dist_path}/tests'
    _EXTRA_TEST_FILES = ['tests/conftest.py']

    def test_as_library_with_no_transformers(self, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_library_config(transformers=None, test_path=test_path)

        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)

    def test_as_library_with_all_transformers(self, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_library_config(transformers=ALL_TRANSFORMERS, test_path=test_path)

        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)

    @per_transformer()
    def test_as_library_with_each_transformer_individually(self, transformer, cli_runner, tmp_path, results_bag):
        test_path = self._create_test_path(tmp_path)
        config = self._create_library_config(transformers=[transformer], test_path=test_path)

        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, results_bag=results_bag)

