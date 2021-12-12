from __future__ import annotations

from typing import Union, List, Iterable

from libcst import MetadataWrapper, CSTNode, Name, Attribute, ClassDef, FunctionDef
from libcst.metadata import ScopeProvider, ExpressionContextProvider, Scope, ParentNodeProvider, ClassScope

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule, PythonModuleCst
from snakepack.config.options import Selectable
from snakepack.config.types import Selector, FullyQualifiedPythonName


class ScopeAnalyzer(PythonModuleCstAnalyzer):
    def analyse(self, subject: Union[Asset, AssetGroup]) -> ScopeAnalyzer.Analysis:
        if isinstance(subject, PythonModule):
            metadata = subject.content.metadata_wrapper.resolve_many([
                ScopeProvider,
                ParentNodeProvider
            ])

            return ScopeAnalyzer.Analysis(
                modules_metadata={
                    subject: metadata
                }
            )
        else:
            raise NotImplementedError

    class Analysis(PythonModuleCstAnalyzer.Analysis):
        def get_fully_qualified_names(
                self, module: PythonModule, node: Union[Name, Attribute, ClassDef, FunctionDef]
        ) -> Iterable[FullyQualifiedPythonName]:
            qualnames = self._modules_metadata[module][ScopeProvider][node].get_qualified_names_for(node)

            return set(
                map(
                    lambda x: FullyQualifiedPythonName(f"{module.full_name}:{x.name.replace('<locals>.', '')}"),
                    qualnames
                )
            )

        def is_attribute(self, module: PythonModule, node: Name) -> bool:
            return (
                    isinstance(self._modules_metadata[module][ParentNodeProvider][node], Attribute)
                    or isinstance(self.get_scope_for_node(module, node), ClassScope)
            )

        def get_scope_for_node(self, module: PythonModule, node: CSTNode) -> Scope:
            current_node = node

            while True:
                if current_node in self._modules_metadata[module][ScopeProvider]:
                    return self._modules_metadata[module][ScopeProvider][current_node]

                current_node = self._modules_metadata[module][ParentNodeProvider][current_node]

    __config_name__ = 'scope'


class Identifier(Selectable):
    def __init__(self, name: str, scopes: List[Scope]):
        self._name = name
        self._scopes = scopes

    @property
    def name(self) -> str:
        return self._name

    @property
    def scope(self) -> List[Scope]:
        return self._scopes

    def matches(self, selector: Selector) -> bool:
        if not isinstance(selector, FullyQualifiedPythonName):
            return False
