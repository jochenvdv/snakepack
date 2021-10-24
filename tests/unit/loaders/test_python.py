from pathlib import Path

import pytest
from modulegraph2 import ModuleGraph

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

    @pytest.mark.skip('TODO')
    def test_load(self, mocker):
        module_graph_constructor = mocker.patch('modulegraph2._modulegraph.ModuleGraph', )
        module_graph = mocker.MagicMock(spec=ModuleGraph)
        module_graph_constructor.return_value = module_graph

        loader = ImportGraphLoader(entry_point=Path('test.py'))
        assets = loader.load()
