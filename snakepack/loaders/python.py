from functools import partial
from pathlib import Path
from typing import Mapping, Dict

from modulegraph2 import ModuleGraph, BaseNode, SourceModule

from snakepack.assets import Asset
from snakepack.assets._base import AssetContentSource, FileContentSource
from snakepack.assets.python import PythonModule
from snakepack.loaders import Loader


class ImportGraphLoader(Loader):
    def __init__(self, entry_point: Path, exclude_stdlib=True):
        self._entry_point = entry_point
        self._exclude_stdlib = exclude_stdlib

    def load(self) -> Mapping[Asset, AssetContentSource]:
        module_graph = ModuleGraph()
        assets = {}

        post_processing_hook = partial(self._process_node, assets=assets)
        module_graph.add_post_processing_hook(post_processing_hook)
        module_graph.add_script(self._entry_point)

        return assets

    @staticmethod
    def _process_node(assets: Dict[Asset, AssetContentSource], graph: ModuleGraph, node: BaseNode):
        if ImportGraphLoader._is_stdlib(node):
            return

        if isinstance(node, SourceModule):
            asset = PythonModule(full_name=node.name)
            content_source = FileContentSource(node.filename)
            assets.put(asset, content_source)

    @staticmethod
    def _is_stdlib(node: BaseNode) -> bool:
        return node.distribution is None
    