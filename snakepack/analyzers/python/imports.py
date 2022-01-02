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
from snakepack.analyzers._base import SubjectAnalyzer, PostLoadingAnalyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup, FileContentSource
from snakepack.assets.python import PythonPackage, PythonApplication, PythonModule, PythonModuleCst
from snakepack.config.types import FullyQualifiedPythonName


class ImportGraphAnalyzer(PostLoadingAnalyzer):
    def __init__(self, module_graph: Optional[ModuleGraph] = None, node_map: Optional[Mapping[PythonModule, Node]] = None):
        self._module_graph = module_graph
        self._modules_metadata = None
        self._node_map = node_map

    def analyse_assets(self, asset_group: AssetGroup) -> Analyzer.Analysis:
        self._modules_metadata = {
            asset: asset.content.metadata_wrapper.resolve_many(self.CST_PROVIDERS)
            for asset in asset_group.deep_assets
            if isinstance(asset, PythonModule)
        }
        self._asset_group = asset_group

        return self.create_analysis()

    def create_analysis(self) -> PythonModuleCstAnalyzer.Analysis:
        return self.Analysis(
            module_graph=self._module_graph,
            node_map=self._node_map,
            import_metadata=self._modules_metadata
        )

    class Analysis(Analyzer.Analysis):
        def __init__(
                self,
                import_metadata: Mapping[PythonModule, Mapping[CSTNode, Iterable[Union[Import, ImportFrom]]]],
                module_graph: Optional[ModuleGraph] = None,
                node_map: Optional[Mapping[PythonModule, Node]] = None,

        ):
            self._module_graph = module_graph
            self._node_map = node_map

            if node_map is None:
                self._inverted_node_map = None
            else:
                self._inverted_node_map = {
                    value: key for key, value in node_map.items()
                }

            self._import_metadata = import_metadata

        @property
        def import_graph_known(self) -> bool:
            return self._module_graph is not None

        @functools.lru_cache()
        def get_importing_modules(self, module: PythonModule, identifier: Optional[str] = None) -> Iterable[PythonModule]:
            assert self.import_graph_known

            importing_nodes = self._module_graph.getReferers(self._node_map[module])
            importing_modules = []

            for importing_node in importing_nodes:
                if importing_node is None:
                    continue

                if isinstance(importing_node, Extension):
                    importing_modules.append(importing_node)
                    continue

                if importing_node not in self._inverted_node_map:
                    # this is the case with the entry point module (Script <> SourceModule), match on filename instead
                    for map_key in self._inverted_node_map:
                        if map_key.filename == importing_node.filename:
                            importing_modules.append(self._inverted_node_map[map_key])
                            break

                    continue

                importing_modules.append(self._inverted_node_map[importing_node])

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
                    modules_importing_identifier.append(importing_module)
                    continue

                if importing_module.content.cst not in self._import_metadata[importing_module]:
                    # assume imported
                    modules_importing_identifier.append(importing_module)
                    continue

                import_stmts = self._import_metadata[importing_module][ImportGraphAnalyzer.ImportProvider][importing_module.content.cst]
                identifier_imported = False

                for import_stmt in import_stmts:
                    if isinstance(import_stmt, Import):
                        for imported_name in import_stmt.names:
                            name = imported_name.name.value if isinstance(imported_name.name, Name) else imported_name.name.attr.value

                            if module.name == name:
                                identifier_imported = True
                                break

                        if identifier_imported:
                            break
                    elif isinstance(import_stmt, ImportFrom):
                        target_module = '.'.join(importing_module.name.split('.')[-1])

                        for relative_dot in import_stmt.relative:
                            target_module = '.'.join(importing_module.name.split('.')[-1])

                        target_module = f'{target_module}.{import_stmt.module}'

                        if target_module != module.name:
                            continue

                        if isinstance(import_stmt.names, ImportStar):
                            identifier_imported = True
                            break

                        for imported_name in import_stmt.names:
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

        @functools.lru_cache()
        def identifier_imported_in_module(self, identifier: str, module: PythonModule) -> bool:
            if module.content.cst not in self._import_metadata[module][ImportGraphAnalyzer.ImportProvider]:
                # assume imported
                return True

            import_stmts = self._import_metadata[module][ImportGraphAnalyzer.ImportProvider][module.content.cst]

            for import_stmt in import_stmts:
                if isinstance(import_stmt, ImportFrom):
                    if isinstance(import_stmt.names, ImportStar):
                        if not self.import_graph_known:
                            # import graph not known and star import -- assume identifier imported
                            return True

                        return True  # TODO
                    else:
                        for imported_name in import_stmt.names:
                            name = imported_name.name.value if isinstance(imported_name.name, Name) else imported_name.name.attr.value

                            if name == identifier:
                                return True

            return False

    class ImportProvider(VisitorMetadataProvider[Iterable[Union[Import, ImportFrom]]]):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._imports = []
            self._module = None

        def visit_Import(self, node: Import) -> Optional[bool]:
            self._imports.append(node)
            self.set_metadata(self._module, self._imports)

        def visit_ImportFrom(self, node: ImportFrom) -> Optional[bool]:
            self._imports.append(node)
            self.set_metadata(self._module, self._imports)

        def visit_Module(self, node: Module) -> Optional[bool]:
            self._module = node

    CST_PROVIDERS = {
        ImportProvider
    }

    __config_name__ = 'import_graph'