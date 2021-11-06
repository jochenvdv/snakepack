import sys
from functools import partial
from pathlib import Path
from site import getsitepackages
from typing import Mapping, Dict, Iterable

from boltons.iterutils import first
from modulegraph.find_modules import find_modules, parse_mf_results
from modulegraph.modulegraph import ModuleGraph, Package, Node
from stdlib_list import stdlib_list

from snakepack.assets import Asset
from snakepack.assets._base import AssetContentSource, FileContentSource
from snakepack.assets.python import PythonModule
from snakepack.config import Options
from snakepack.loaders import Loader


_STDLIB_PATHS = [Path(path) for path in set(sys.path) - set(getsitepackages())]
_STDLIB_MODULES = {}


class ImportGraphLoader(Loader):
    def load(self) -> Iterable[Asset]:
        entry_point_path = self.global_options.source_base_path / self._options.entry_point
        module_graph = find_modules((str(entry_point_path),))
        python_modules, c_extensions = parse_mf_results(module_graph)

        assets = [
            self._create_python_asset(dependency, entry_point_path)
            for dependency in python_modules
            if not self._is_stdlib(
                module_name=dependency.identifier,
                file_path=Path(dependency.filename),
                python_version=self._options.target_version
            )
        ]

        return assets

    @staticmethod
    def _create_python_asset(dependency: Node, entry_path: Path) -> PythonModule:
        if isinstance(dependency, Package):
            asset = PythonModule.from_source(
                full_name=dependency.identifier + '.__init__',
                source=FileContentSource(dependency.filename)
            )
        else:
            if str(entry_path.resolve()) == dependency.identifier:
                name = entry_path.stem

                for parent in entry_path.parents:
                    init_file = parent / '__init__.py'

                    if init_file.exists():
                        name = parent.stem + '.' + name
            else:
                name = dependency.identifier

            asset = PythonModule.from_source(
                full_name=name,
                source=FileContentSource(dependency.filename)
            )

        return asset

    @staticmethod
    def _is_stdlib(module_name: str, file_path: Path, python_version) -> bool:
        global _STDLIB_MODULES

        if python_version not in _STDLIB_MODULES:
            _STDLIB_MODULES[python_version] = set(stdlib_list(str(python_version)))

        return (
                any(map(lambda x: x in file_path.parents, _STDLIB_PATHS))
                and module_name in _STDLIB_MODULES[python_version]
        )

    class Options(Options):
        entry_point: Path
        exclude_stdlib: bool = True
        target_version: str = '3.9'

    __config_name__ = 'import_graph'


__all__ = [
    ImportGraphLoader
]