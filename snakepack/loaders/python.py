from functools import partial
from pathlib import Path
from typing import Mapping, Dict, Iterable

from modulegraph2 import ModuleGraph, BaseNode, SourceModule

from snakepack.assets import Asset
from snakepack.assets._base import AssetContentSource, FileContentSource
from snakepack.assets.python import PythonModule
from snakepack.config import Options
from snakepack.loaders import Loader


class ImportGraphLoader(Loader):
    def load(self) -> Iterable[Asset]:
        module_graph = ModuleGraph()
        assets = []

        post_processing_hook = partial(self._process_node, assets=assets)
        module_graph.add_post_processing_hook(post_processing_hook)
        entry_point_path = self.global_options.source_base_path / self._options.entry_point
        module_graph.add_script(entry_point_path)

        return assets

    @staticmethod
    def _process_node(assets: Iterable[Asset], graph: ModuleGraph, node: BaseNode):
        if ImportGraphLoader._is_stdlib(node):
            return

        if isinstance(node, SourceModule):
            asset = PythonModule.from_source(
                full_name=node.name,
                source=FileContentSource(node.filename)
            )
            assets.append(asset)

    @staticmethod
    def _is_stdlib(node: BaseNode) -> bool:
        return node.distribution is None

    class Options(Options):
        entry_point: Path
        exclude_stdlib: bool = True

    __config_name__ = 'import_graph'