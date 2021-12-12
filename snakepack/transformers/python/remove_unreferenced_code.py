from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, ClassDef, Name, FunctionDef, CSTNode, BaseSmallStatement, Assign, Attribute, AnnAssign
from libcst.metadata import FunctionScope, ClassScope, ComprehensionScope, GlobalScope

from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.transformers.python._base import PythonModuleTransformer


class RemoveUnreferencedCodeTransformer(PythonModuleTransformer):
    REQUIRED_ANALYZERS = PythonModuleTransformer.REQUIRED_ANALYZERS + [
        ScopeAnalyzer,
        ImportGraphAnalyzer
    ]

    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_FunctionDef(
                self, original_node: FunctionDef, updated_node: FunctionDef
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            if not self._is_referenced(original_node, updated_node.name.value):
                return RemovalSentinel.REMOVE

            return updated_node

        def leave_ClassDef(
                self, original_node: ClassDef, updated_node: ClassDef
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            if not self._is_referenced(original_node, updated_node.name.value):
                return RemovalSentinel.REMOVE

            return updated_node

        def leave_Assign(
                self, original_node: Assign, updated_node: Assign
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            if len(updated_node.targets) > 1:
                # don't touch multi-assignments (need type inference for reliably remove)
                return updated_node

            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(self._subject, original_node)

            if not isinstance(updated_node.targets[0].target, Name) or isinstance(scope, ClassScope):
                # don't touch attributes (references not reliably detected)
                return updated_node

            if not self._is_referenced(original_node.targets[0].target, updated_node.targets[0].target.value):
                return RemovalSentinel.REMOVE

            return updated_node

        def leave_AnnAssign(
                self, original_node: AnnAssign, updated_node: AnnAssign
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(self._subject, original_node)

            if not isinstance(updated_node.target, Name) or isinstance(scope, ClassScope):
                # don't touch attributes (references not reliably detected)
                return updated_node

            if not self._is_referenced(original_node.target, updated_node.target.value):
                return RemovalSentinel.REMOVE

            return updated_node

        def _is_referenced(self, node: CSTNode, identifier: str) -> bool:
            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(self._subject, node)
            assert identifier in scope

            if identifier in scope.accesses:
                return True

            if isinstance(scope, GlobalScope):
                return len(self._analyses[ImportGraphAnalyzer].get_importing_modules(self._subject, identifier)) > 0

            return False

    __config_name__ = 'remove_unreferenced_code'

