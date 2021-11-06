from pathlib import Path

import pytest

from snakepack.config import GlobalOptions
from snakepack.loaders.python import ImportGraphLoader


class ImportGraphLoaderTest:
    def test_config_name(self):
        assert ImportGraphLoader.__config_name__ == 'import_graph'

    def test_init(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        options = ImportGraphLoader.Options(entry_point='test', exclude_stdlib=True)
        loader = ImportGraphLoader(global_options=global_options, options=options)

    def test_init_default_options(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        options = ImportGraphLoader.Options(entry_point='test')
        loader = ImportGraphLoader(global_options=global_options, options=options)

        assert loader.options.exclude_stdlib is True
