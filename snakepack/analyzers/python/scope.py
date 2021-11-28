from __future__ import annotations

from typing import Union, List, Iterable

from libcst import MetadataWrapper, CSTNode, Name, Attribute, ClassDef, FunctionDef
from libcst.metadata import ScopeProvider, ExpressionContextProvider, Scope

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule, PythonModuleCst
from snakepack.config.options import Selectable
from snakepack.config.types import Selector, FullyQualifiedPythonName


class ScopeAnalyzer(PythonModuleCstAnalyzer):
    def analyse(self, subject: Union[Asset, AssetGroup]) -> ScopeAnalyzer.Analysis:
        if isinstance(subject, PythonModule):
            metadata = subject.content.metadata_wrapper.resolve(ScopeProvider)

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
            qualnames = self._modules_metadata[module][node].get_qualified_names_for(node)

            return set(
                map(
                    lambda x: FullyQualifiedPythonName(f"{module.full_name}:{x.name.replace('<locals>.', '')}"),
                    qualnames
                )
            )


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
