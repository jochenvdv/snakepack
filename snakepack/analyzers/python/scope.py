from __future__ import annotations

import functools
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
    CST_PROVIDERS = {
        ScopeProvider,
        ParentNodeProvider
    }

    def analyse_subject(self, subject: Union[Asset, AssetGroup]) -> ScopeAnalyzer.Analysis:
        if isinstance(subject, PythonModule):
            metadata = subject.content.metadata_wrapper.resolve_many(self.CST_PROVIDERS)

            return self.create_analysis(metadata)
        else:
            raise NotImplementedError

    class Analysis(PythonModuleCstAnalyzer.Analysis):
        @functools.cache
        def get_fully_qualified_names(
                self, module: PythonModule, node: Union[Name, Attribute, ClassDef, FunctionDef]
        ) -> Iterable[FullyQualifiedPythonName]:
            qualnames = self._metadata[ScopeProvider][node].get_qualified_names_for(node)

            return set(
                map(
                    lambda x: FullyQualifiedPythonName(f"{module.full_name}:{x.name.replace('<locals>.', '')}"),
                    qualnames
                )
            )

        @functools.cache
        def is_attribute(self, node: Name) -> bool:
            return (
                    isinstance(self._metadata[ParentNodeProvider][node], Attribute)
                    or isinstance(self.get_scope_for_node(node), ClassScope)
            )

        @functools.cache
        def get_scope_for_node(self, node: CSTNode) -> Scope:
            current_node = node

            while True:
                if current_node in self._metadata[ScopeProvider]:
                    return self._metadata[ScopeProvider][current_node]

                current_node = self._metadata[ParentNodeProvider][current_node]

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
