import sys
from collections import defaultdict
from functools import reduce
from operator import getitem

from pathlib import Path
from site import getsitepackages

from modulegraph.find_modules import find_modules, parse_mf_results
from modulegraph.modulegraph import ModuleGraph, Package, Node
from stdlib_list import stdlib_list

from snakepack.assets._base import FileContentSource
from snakepack.assets.python import PythonModule, PythonApplication, PythonPackage
from snakepack.config import Options
from snakepack.loaders import Loader


_STDLIB_PATHS = [Path(path) for path in set(sys.path) - set(getsitepackages())]
_STDLIB_MODULES = {}


class ImportGraphLoader(Loader):
    def load(self) -> PythonApplication:
        entry_point_path = self.global_options.source_base_path / self._options.entry_point
        module_graph = find_modules((str(entry_point_path),))
        python_modules, c_extensions = parse_mf_results(module_graph)

        entry_point = None
        modules = []

        pkg_dict = {}

        for python_module in python_modules:
            if not self._is_stdlib(
                module_name=python_module.identifier,
                file_path=Path(python_module.filename),
                python_version=self._options.target_version
            ):
                module = self._create_python_dep(python_module, entry_point_path)
                module_path_segments = module.full_name.split('.')
                pkg_name = '.'.join(module_path_segments[:-1])
                module_name = module_path_segments[-1]

                if module.source.path == str(entry_point_path.resolve()):
                    entry_point = module

                if len(pkg_name) > 0:
                    # module is in a package
                    if not pkg_name in pkg_dict:
                        pkg_dict[pkg_name] = []

                    pkg_dict[pkg_name].append(module)
                else:
                    # module is not in a package
                    modules.append(module)

        assert entry_point is not None, 'Didn\t encounter entry point module in import graph'

        pkg_obj_dict = {}

        for pkg_name, pkg_modules in pkg_dict.items():
            pkg_obj_dict[pkg_name] = PythonPackage(
                full_name=pkg_name,
                modules=pkg_modules,
                subpackages=[]
            )

        for pkg_name, pkg_obj in pkg_obj_dict.items():
            parent_pkg_name = '.'.join(pkg_obj.full_name.split('.')[:-1])

            if len(parent_pkg_name) > 0:
                # register subpackage with parent
                pkg_obj_dict[parent_pkg_name].subgroups.append(pkg_obj)

        packages = [
            package
            for package in pkg_obj_dict.values()
            if len(package.full_name.split('.')) == 1
        ]

        return PythonApplication(
            entry_point=entry_point,
            packages=packages,
            modules=modules
        )

    @staticmethod
    def _create_python_dep(dependency: Node, entry_path: Path) -> PythonModule:
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