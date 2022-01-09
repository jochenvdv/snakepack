import functools
import sys
from collections import defaultdict
from functools import reduce
from importlib.machinery import all_suffixes
from importlib.resources import is_resource
from operator import getitem

from pathlib import Path
from site import getsitepackages
from typing import List, Iterable, Optional

from modulegraph.find_modules import find_modules, parse_mf_results
from modulegraph.modulegraph import ModuleGraph, Package, Node
from stdlib_list import stdlib_list

from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.assets._base import FileContentSource
from snakepack.assets.generic import StaticFile
from snakepack.assets.python import PythonModule, PythonApplication, PythonPackage, PythonModuleCst
from snakepack.config.options import Options
from snakepack.config.types import FullyQualifiedPythonName
from snakepack.loaders import Loader


_STDLIB_PATHS = [Path(path) for path in set(sys.path) - set(getsitepackages())]
_STDLIB_MODULES = {}


class ImportGraphLoader(Loader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analysis = None

    @property
    def analysis(self) -> ImportGraphAnalyzer.Analysis:
        return self._analysis

    def load(self) -> PythonApplication:
        entry_point_path = self.global_options.source_base_path / self._options.entry_point
        module_graph = find_modules((str(entry_point_path),), includes=self._options.includes)
        python_modules, c_extensions = parse_mf_results(module_graph)

        entry_point = None
        modules = []

        pkg_dict = {}
        node_map = {}

        for python_module in python_modules:
            if not self._is_stdlib(
                    module_name=python_module.identifier,
                    file_path=Path(python_module.filename),
                    python_version=self._options.target_version
            ):
                module = self._create_python_dep(python_module, entry_point_path)
                module_path_segments = module.name.split('.')
                pkg_name = '.'.join(module_path_segments[:-1])
                module_name = module_path_segments[-1]

                if module.source.path == str(entry_point_path.resolve()):
                    entry_point = module

                if len(pkg_name) > 0:
                    # module is in a package
                    pkg_path = Path(module.source.path).parent

                    if not (pkg_name, pkg_path) in pkg_dict:
                        pkg_dict[(pkg_name, pkg_path)] = []

                    pkg_dict[(pkg_name, pkg_path)].append(module)
                else:
                    # module is not in a package
                    modules.append(module)

                node_map[module] = python_module

        assert entry_point is not None, 'Didn\t encounter entry point module in import graph'

        pkg_obj_dict = {}

        for pkg_name_and_path, pkg_modules in pkg_dict.items():
            pkg_name, pkg_path = pkg_name_and_path
            data_files = []

            if self._options.load_data_files:
                data_files = self._get_data_files(pkg_path, pkg_path)

            pkg_obj_dict[pkg_name] = PythonPackage(
                full_name=pkg_name,
                modules=pkg_modules,
                subpackages=[],
                data_files=data_files
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

        application = PythonApplication(
            entry_point=entry_point,
            packages=packages,
            modules=modules
        )

        analyzer = ImportGraphAnalyzer(
            module_graph=module_graph,
            node_map=node_map
        )

        self._analysis = analyzer.analyse_assets(application)

        return application

    def _get_data_files(self, root_path, path) -> Iterable[Path]:
        files = set()

        for sub_path in path.iterdir():
            if sub_path.is_file() and _is_data_file(sub_path):
                static_file_path = sub_path.relative_to(root_path.parent)
                static_file = StaticFile.from_source(
                    name=static_file_path,
                    target_path=static_file_path,
                    source=FileContentSource(
                        path=sub_path,
                        binary=True
                    )
                )
                files.add(static_file)
            elif sub_path.is_dir() and _is_data_file_dir(sub_path):
                files.update(self._get_data_files(root_path, sub_path))

        return files

    @staticmethod
    def _create_python_dep(dependency: Node, entry_path: Path) -> PythonModule:
        if isinstance(dependency, Package):
            asset = PythonModule.from_source(
                name=dependency.identifier + '.__init__',
                source=FileContentSource(dependency.filename, default_content_type=PythonModuleCst)
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
                name=name,
                source=FileContentSource(dependency.filename, default_content_type=PythonModuleCst)
            )

        return asset

    @staticmethod
    @functools.lru_cache()
    def _is_stdlib(module_name: str, file_path: Path, python_version) -> bool:
        global _STDLIB_MODULES

        if python_version not in _STDLIB_MODULES:
            _STDLIB_MODULES[python_version] = set(stdlib_list(str(python_version)))
            _STDLIB_MODULES[python_version].add('sitecustomize')

        return (
                any(map(lambda x: x in file_path.parents, _STDLIB_PATHS))
                and module_name in _STDLIB_MODULES[python_version]
        )

    class Options(Options):
        entry_point: Path
        exclude_stdlib: bool = True
        target_version: str = '3.9'
        includes: List[FullyQualifiedPythonName] = []
        load_data_files: bool = True

    __config_name__ = 'import_graph'


class PackageLoader(Loader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analysis = None

    def load(self) -> PythonPackage:
        pkg_name = self._options.pkg_name.module_path[0]
        pkg_path = self._global_options.source_base_path

        if self._options.pkg_base_path is not None:
            pkg_path = pkg_path / self._options.pkg_base_path

        pkg_path = pkg_path / pkg_name

        python_pkg = self._load_package(pkg_name, pkg_path)
        analyzer = ImportGraphAnalyzer()
        self._analysis = analyzer.analyse_assets(python_pkg)

        return python_pkg

    @property
    def analysis(self) -> ImportGraphAnalyzer.Analysis:
        return self._analysis

    def _load_package(self, pkg_name, pkg_path: Path):
        subpackages = []
        modules = []
        data_files = []
        package = PythonPackage(full_name=pkg_name, subpackages=subpackages, modules=modules, data_files=data_files)

        for path in pkg_path.iterdir():
            full_name = f'{pkg_name}.{path.stem}'

            if path.is_dir() and (path / '__init__.py').is_file() and _is_data_file_dir(path):
                # subpackage
                subpackages.append(self._load_package(full_name, path))
            elif path.suffix == '.py':
                # module
                modules.append(
                    PythonModule.from_source(
                        name=full_name,
                        source=FileContentSource(path=path, default_content_type=PythonModuleCst)
                    )
                )
            elif self._options.load_data_files and _is_data_file(path):
                static_file_path = Path(f"{package.full_name.replace('.', '/')}/{path.name}")
                data_files.append(
                    StaticFile.from_source(
                        name=str(static_file_path),
                        target_path=static_file_path,
                        source=FileContentSource(
                            path=path,
                            binary=True
                        )
                    )
                )

        return package

    class Options(Options):
        pkg_name: FullyQualifiedPythonName
        pkg_base_path: Optional[Path] = None
        target_version: str = '3.9'
        load_data_files: bool = True

    __config_name__ = 'package'


def _is_data_file(path: Path) -> bool:
    return path.is_file() and not any(path.name.endswith(sfx) for sfx in all_suffixes())


def _is_data_file_dir(path: Path):
    return path.is_dir() and path.name != '__pycache__'


__all__ = [
    ImportGraphLoader,
    PackageLoader
]