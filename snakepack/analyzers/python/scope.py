from __future__ import annotations

import functools
from typing import Union, List, Iterable, Optional

from libcst import MetadataWrapper, CSTNode, Name, Attribute, ClassDef, FunctionDef, Param, Annotation, Arg, \
    VisitorMetadataProvider, Global, Nonlocal, Call, Module
from libcst.metadata import ScopeProvider, ExpressionContextProvider, Scope, ParentNodeProvider, ClassScope, \
    ComprehensionScope, FunctionScope, GlobalScope

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.assets import Asset, AssetGroup
from snakepack.assets.python import PythonModule, PythonModuleCst
from snakepack.config.options import Selectable
from snakepack.config.types import Selector, FullyQualifiedPythonName


class ScopeAnalyzer(PythonModuleCstAnalyzer):
    def analyse_subject(self, subject: Union[Asset, AssetGroup]) -> ScopeAnalyzer.Analysis:
        if isinstance(subject, PythonModule):
            metadata = subject.content.metadata_wrapper.resolve_many(self.CST_PROVIDERS)

            return self.create_analysis(metadata)
        else:
            raise NotImplementedError

    class Analysis(PythonModuleCstAnalyzer.Analysis):
        @functools.lru_cache()
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

        @functools.lru_cache()
        def is_attribute(self, node: Name) -> bool:
            return (
                    isinstance(self._metadata[ParentNodeProvider][node], Attribute)
                    or isinstance(self.get_scope_for_node(node), ClassScope)
            )

        @functools.lru_cache()
        def get_scope_for_node(self, node: CSTNode) -> Scope:
            current_node = node

            while True:
                if current_node in self._metadata[ScopeProvider]:
                    return self._metadata[ScopeProvider][current_node]

                current_node = self._metadata[ParentNodeProvider][current_node]

        @functools.lru_cache()
        def is_in_local_scope(self, node: CSTNode) -> bool:
            scope = self.get_scope_for_node(node)

            if not isinstance(scope, (FunctionScope)):
                # global and class scope are never considered local scope
                return False

            if isinstance(self._metadata[ParentNodeProvider][node], Param):
                # function parameter names are not considered local scope (they are part of the API to the parent scope)
                return False

            for assignment in scope.assignments[node]:
                # identifiers that refer to parameters that are considered non-local scope are also non-local
                if isinstance(assignment.node, Param):
                    return False

            return True

        @functools.lru_cache()
        def is_type_annotation(self, node: CSTNode) -> bool:
            return isinstance(self._metadata[ParentNodeProvider][node], Annotation)

        @functools.lru_cache()
        def is_keyword_arg(self, node: CSTNode) -> bool:
            parent = self._metadata[ParentNodeProvider][node]
            return isinstance(parent, Arg) and parent.keyword is node

        @functools.lru_cache()
        def uses_globals_builtin(self, module: Module) -> bool:
            return self._metadata[ScopeAnalyzer._GlobalsLocalsProvider][module]['uses_globals_builtin']

        @functools.lru_cache()
        def uses_locals_builtin(self, module: Module) -> bool:
            return self._metadata[ScopeAnalyzer._GlobalsLocalsProvider][module]['uses_locals_builtin']

        @functools.lru_cache()
        def uses_global_stmt(self, module: Module) -> bool:
            return self._metadata[ScopeAnalyzer._GlobalsLocalsProvider][module]['uses_global_stmt']

        @functools.lru_cache()
        def uses_nonlocal_stmt(self, module: Module) -> bool:
            return self._metadata[ScopeAnalyzer._GlobalsLocalsProvider][module]['uses_nonlocal_stmt']

        @functools.lru_cache()
        def get_all_scopes(self) -> Iterable[Scope]:
            return set(self._metadata[ScopeProvider].values())

    class _GlobalsLocalsProvider(VisitorMetadataProvider):
        def __init__(self, *args, **kwargs):
            self._uses_global_stmt = False
            self._uses_nonlocal_stmt = False
            self._uses_globals_builtin = False
            self._uses_locals_builtin = False
            super().__init__(*args, **kwargs)

        def visit_Global(self, node: Global) -> Optional[bool]:
            self._uses_global_stmt = True

        def visit_Nonlocal(self, node: Nonlocal) -> Optional[bool]:
            self._uses_nonlocal_stmt = True

        def visit_Call(self, node: Call) -> Optional[bool]:
            if isinstance(node.func, Name) and node.func.value == 'globals':
                self._uses_globals_builtin = True
            elif isinstance(node.func, Name) and node.func.value == 'locals':
                self._uses_locals_builtin = True

        def visit_Module(self, node: Module) -> Optional[bool]:
            self.set_metadata(node, {
                'uses_global_stmt': self._uses_global_stmt,
                'uses_nonlocal_stmt': self._uses_nonlocal_stmt,
                'uses_globals_builtin': self._uses_globals_builtin,
                'uses_locals_builtin': self._uses_locals_builtin
            })

    CST_PROVIDERS = {
        ScopeProvider,
        ParentNodeProvider,
        _GlobalsLocalsProvider
    }

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
