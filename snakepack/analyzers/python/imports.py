import functools
import sys
from pathlib import Path
from site import getsitepackages
from typing import Union, Iterable, Mapping, Optional

from libcst import VisitorMetadataProvider, Import, ImportFrom, Module, MetadataWrapper, CSTNode, ImportStar, Name, \
    Attribute
from modulegraph.find_modules import find_modules, parse_mf_results
from modulegraph.modulegraph import ModuleGraph, Package, Node, Extension, SourceModule
from stdlib_list import stdlib_list

from snakepack.analyzers import Analyzer
from snakepack.analyzers._base import PreLoadingAnalyzer, SubjectAnalyzer, PostLoadingAnalyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup, FileContentSource
from snakepack.assets.python import PythonPackage, PythonApplication, PythonModule, PythonModuleCst
from snakepack.config.types import FullyQualifiedPythonName

_STDLIB_PATHS = [Path(path) for path in set(sys.path) - set(getsitepackages())]
_STDLIB_MODULES = {}


class ImportGraphAnalyzer(PreLoadingAnalyzer, PostLoadingAnalyzer):
    def __init__(self, entry_point_path: Optional[Path], target_version: str, includes: Optional[Iterable[FullyQualifiedPythonName]]=None):
        self._entry_point_path = entry_point_path

        if includes is None:
            self._includes = []
        else:
            self._includes = includes

        self._target_version = target_version
        self._asset_group = None
        self._module_graph = None
        self._modules_metadata = None
        self._node_map = None

    def analyse(self) -> Analyzer.Analysis:
        assert self._entry_point_path is not None

        self._module_graph = find_modules((str(self._entry_point_path),), includes=self._includes)
        python_modules, c_extensions = parse_mf_results(self._module_graph)

        entry_point = None
        modules = []

        pkg_dict = {}
        self._node_map = {}

        for python_module in python_modules:
            if not self._is_stdlib(
                    module_name=python_module.identifier,
                    file_path=Path(python_module.filename),
                    python_version=self._target_version
            ):
                module = self._create_python_dep(python_module, self._entry_point_path)
                module_path_segments = module.full_name.split('.')
                pkg_name = '.'.join(module_path_segments[:-1])
                module_name = module_path_segments[-1]

                if module.source.path == str(self._entry_point_path.resolve()):
                    entry_point = module

                if len(pkg_name) > 0:
                    # module is in a package
                    if not pkg_name in pkg_dict:
                        pkg_dict[pkg_name] = []

                    pkg_dict[pkg_name].append(module)
                else:
                    # module is not in a package
                    modules.append(module)

                self._node_map[module] = python_module

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

        self._asset_group = PythonApplication(
            entry_point=entry_point,
            packages=packages,
            modules=modules
        )

        return self.create_analysis()

    def analyse_assets(self, asset_group: AssetGroup) -> Analyzer.Analysis:
        self._modules_metadata = {
            module: module.content.metadata_wrapper.resolve_many(self.CST_PROVIDERS)
            for module in asset_group.deep_assets
        }
        self._asset_group = asset_group

        return self.create_analysis()

    def create_analysis(self) -> PythonModuleCstAnalyzer.Analysis:
        return self.Analysis(
            module_graph=self._module_graph,
            asset_group=self._asset_group,
            node_map=self._node_map,
            import_metadata=self._modules_metadata
        )

    @staticmethod
    def _create_python_dep(dependency: Node, entry_path: Path) -> PythonModule:
        if isinstance(dependency, Package):
            asset = PythonModule.from_source(
                full_name=dependency.identifier + '.__init__',
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
                full_name=name,
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

    class Analysis(Analyzer.Analysis):
        def __init__(
                self,
                module_graph: ModuleGraph,
                asset_group: Optional[AssetGroup],
                node_map: Mapping[PythonModule, Node],
                import_metadata: Mapping[PythonModule, Mapping[CSTNode, Iterable[Union[Import, ImportFrom]]]]
        ):
            self._module_graph = module_graph
            self._asset_group = asset_group
            self._node_map = node_map

            if node_map is None:
                self._inverted_node_map = None
            else:
                self._inverted_node_map = {
                    value: key for key, value in node_map.items()
                }

            self._import_metadata = import_metadata

        @property
        def asset_group(self) -> Optional[PythonApplication]:
            return self._asset_group

        @property
        def module_graph(self):
            return self._module_graph

        @property
        def import_graph_known(self) -> bool:
            return self._module_graph is not None

        @functools.lru_cache()
        def get_importing_modules(self, module: PythonModule, identifier: Optional[str] = None) -> Iterable[PythonModule]:
            assert self.import_graph_known

            importing_nodes = self._module_graph.getReferers(self._node_map[module])
            importing_modules = [
                    self._inverted_node_map[importing_node] if not isinstance(importing_node, Extension) else importing_node
                    for importing_node in importing_nodes if importing_node is not None
                ]

            if identifier is None:
                return importing_modules

            modules_importing_identifier = []

            for importing_module in importing_modules:
                if isinstance(importing_module, Extension):
                    # cannot analyze C extensions, assume identifier is imported
                    identifier_imported = True
                    break

                import_stmts = self._import_metadata[importing_module][ImportGraphAnalyzer.ImportProvider]
                identifier_imported = False

                for import_stmt in import_stmts:
                    if isinstance(import_stmt, Import):
                        for imported_name in import_stmt.names:
                            name = imported_name.name.value if isinstance(imported_name.name, Name) else imported_name.name.attr.value

                            if module.full_name == name:
                                identifier_imported = True
                                break

                        if identifier_imported:
                            break
                    elif isinstance(import_stmt, ImportFrom):
                        target_module = '.'.join(importing_module.full_name.split('.')[-1])

                        for relative_dot in import_stmt.relative:
                            target_module = '.'.join(importing_module.full_name.split('.')[-1])

                        target_module = f'{target_module}.{import_stmt.module}'

                        if target_module != module.full_name:
                            continue

                        for imported_name in import_stmt.names:
                            if isinstance(imported_name, ImportStar):
                                identifier_imported = True
                                break

                            for import_alias in imported_name:
                                name = imported_name.value if isinstance(imported_name, Name) else imported_name.attr.value

                                if name == identifier:
                                    identifier_imported = True
                                    break

                            if identifier_imported:
                                break

                        if identifier_imported:
                            break

                if identifier_imported:
                    modules_importing_identifier.append(importing_module)

            return modules_importing_identifier

    class ImportProvider(VisitorMetadataProvider[Iterable[Union[Import, ImportFrom]]]):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._imports = []

        def visit_Import(self, node: Import) -> Optional[bool]:
            self._imports.append(node)

        def visit_ImportFrom(self, node: ImportFrom) -> Optional[bool]:
            self._imports.append(node)

        def visit_Module(self, node: Module) -> Optional[bool]:
            self.set_metadata(node, self._imports)

    CST_PROVIDERS = {
        ImportProvider
    }

    __config_name__ = 'import_graph'