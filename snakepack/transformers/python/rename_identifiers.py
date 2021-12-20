from typing import Optional, Union, Dict, Mapping, Type

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, Name, BaseExpression, CSTNode, Import, ImportFrom
from libcst.metadata import ExpressionContextProvider, ExpressionContext, ScopeProvider, ParentNodeProvider

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets import AssetGroup
from snakepack.assets.python import PythonModule, Python, PythonModuleCst
from snakepack.transformers.python._base import PythonModuleTransformer
from snakepack.transformers.python._renaming import NameRegistry


class RenameIdentifiersTransformer(PythonModuleTransformer):
    REQUIRED_ANALYZERS = PythonModuleTransformer.REQUIRED_ANALYZERS + [
        ScopeAnalyzer,
        ImportGraphAnalyzer
    ]

    def transform(
            self,
            analyses: Mapping[Type[Analyzer], Analyzer.Analysis],
            subject: Union[PythonModule, AssetGroup[Python]]
    ) -> Union[PythonModule, AssetGroup[Python]]:
        if isinstance(subject, PythonModule):
            transformer = self._CstTransformer(
                subject=subject,
                options=self._options,
                analyses=analyses,
                transformer=self
            )
            subject.content = PythonModuleCst(cst=subject.content.cst.visit(transformer))

        return subject

    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._name_registry = NameRegistry()
            self._renames: Dict[CSTNode, str] = {}
            self._accesses: Dict[CSTNode, str] = {}

        def visit_Import(self, node: Import) -> Optional[bool]:
            # don't rename import identifiers
            return False

        def visit_ImportFrom(self, node: ImportFrom) -> Optional[bool]:
            # don't rename import identifiers
            return False

        def visit_Name(self, node: Name) -> Optional[bool]:
            if node in self._renames:
                # already marked this identifier to be renamed
                return

            if self._analyses[ScopeAnalyzer].is_attribute(node):
                # don't rename class attributes (nearly impossible to find all references through static analysis)
                return

            if len(self._analyses[ImportGraphAnalyzer].get_importing_modules(self._subject, node.value)) > 0:
                # don't rename because this identifier is imported in another module
                return

            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(node)

            for assignment in scope.assignments[node]:
                if assignment.name is node.value:
                    new_name = None

                    while new_name is None or (new_name != node.value and len(scope.accesses[new_name]) > 0):
                        # generate new name that is not referenced yet in the current scope
                        new_name = self._name_registry.generate_name_for_scope(scope=scope)

                    self._renames[node] = new_name
                    self._name_registry.register_name_for_scope(scope=scope, name=new_name)

                    for access in assignment.references:
                        self._renames[access.node] = new_name

        def leave_Name(self, original_node: Name, updated_node: Name) -> BaseExpression:
            if original_node in self._renames:
                return updated_node.with_changes(value=self._renames[original_node])

            return updated_node


    __config_name__ = 'rename_identifiers'
