from typing import Optional, Union, Dict, Mapping, Type

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, Name, BaseExpression, CSTNode
from libcst.metadata import ExpressionContextProvider, ExpressionContext, ScopeProvider

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets import AssetGroup
from snakepack.assets.python import PythonModule, Python, PythonModuleCst
from snakepack.transformers.python._base import PythonModuleTransformer
from snakepack.transformers.python._renaming import NameRegistry


class RenameIdentifiersTransformer(PythonModuleTransformer):
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

        def visit_Name(self, node: Name) -> Optional[bool]:
            if node in self._renames:
                return

            scope = self._analyses[ScopeAnalyzer][self._subject][node]

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
