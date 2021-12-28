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
        config = self._create_application_config(tmp_path=tmp_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, tmp_path=tmp_path)

    @per_transformer()
    def test_snakepack_as_application_each_transformer_individually(self, transformer, cli_runner, tmp_path):
        config = self._create_application_config(transformer=transformer, tmp_path=tmp_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, tmp_path=tmp_path)

    @pytest.mark.skip
    def test_snakepack_as_library_with_all_transformers(self, cli_runner, tmp_path):
        config = self._create_library_config(tmp_path=tmp_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, tmp_path=tmp_path)

    @pytest.mark.skip
    @per_transformer()
    def test_snakepack_as_library_each_transformer_individually(self, transformer, cli_runner, tmp_path):
        config = self._create_library_config(transformer=transformer, tmp_path=tmp_path)
        self._test_snakepack(config=config, cli_runner=cli_runner, tmp_path=tmp_path)
