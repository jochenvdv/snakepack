from pathlib import Path

import pytest
from modulegraph2 import ModuleGraph

from snakepack.loaders.python import ImportGraphLoader


class ImportGraphLoaderTest:
    def test_init(self):
        loader = ImportGraphLoader(entry_point=Path('test.py'))

    @pytest.mark.skip('TODO')
    def test_load(self, mocker):
        module_graph_constructor = mocker.patch('modulegraph2._modulegraph.ModuleGraph', )
        module_graph = mocker.MagicMock(spec=ModuleGraph)
        module_graph_constructor.return_value = module_graph

        loader = ImportGraphLoader(entry_point=Path('test.py'))
        assets = loader.load()
