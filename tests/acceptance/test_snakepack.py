from pathlib import Path

import pytest

from snakepack.app import snakepack
from tests.acceptance._base import BaseAcceptanceTest, per_transformer


class SnakepackAcceptanceTest(BaseAcceptanceTest):
    _SUBJECT_NAME = 'snakepack'
    _SOURCEDIR = Path(__file__).resolve().parent.parent.parent
    _APPLICATION_ENTRY_POINT = 'snakepack/__main__.py'
    _LIBRARY_PACKAGE = 'snakepack'

    def test_snakepack_as_application_with_all_transformers(self, cli_runner, tmp_path):
        test_path = self._create_test_path(tmp_path)
        config = self._create_application_config(test_path=test_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path)
        self._test_application_compiled_output(test_path=test_path, cli_runner=cli_runner)

    @pytest.mark.skip
    @per_transformer()
    def test_snakepack_as_application_each_transformer_individually(self, transformer, cli_runner, tmp_path):
        test_path = self._create_test_path(tmp_path)
        config = self._create_application_config(transformer=transformer, test_path=test_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path)
        self._test_application_compiled_output(test_path=test_path, cli_runner=cli_runner)

    def test_snakepack_as_library_with_all_transformers(self, cli_runner, tmp_path):
        test_path = self._create_test_path(tmp_path)
        config = self._create_library_config(test_path=test_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path)

    @pytest.mark.skip
    @per_transformer()
    def test_snakepack_as_library_each_transformer_individually(self, transformer, cli_runner, tmp_path):
        test_path = self._create_test_path(tmp_path)
        config = self._create_library_config(transformer=transformer, test_path=test_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path)

    def _test_application_compiled_output(self, test_path, cli_runner):
        config = self._create_application_config(test_path=test_path, roundtrip=True)
        self._test_snakepack(config=config, cli_runner=cli_runner, test_path=test_path, roundtrip=True)

    def _test_library_compiled_output(self):
        pass