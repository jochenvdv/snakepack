from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, ClassDef, Name, FunctionDef, CSTNode, BaseSmallStatement, Assign, Attribute, AnnAssign, Import, \
    Tuple, List, ImportFrom, ImportStar
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
            if not self._is_referenced(original_node, updated_node.name.value, assignment=False):
                return RemovalSentinel.REMOVE

            return updated_node

        def leave_ClassDef(
                self, original_node: ClassDef, updated_node: ClassDef
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            if not self._is_referenced(original_node, updated_node.name.value, assignment=False):
                return RemovalSentinel.REMOVE

            return updated_node

        def leave_Assign(
                self, original_node: Assign, updated_node: Assign
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            if len(updated_node.targets) > 1:
                # don't touch multi-assignments (need type inference for reliably remove)
                return updated_node

            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(original_node)

            if not isinstance(updated_node.targets[0].target, Name) or isinstance(scope, ClassScope):
                # don't touch attributes (references not reliably detected)
                return updated_node

            if not self._is_referenced(original_node.targets[0].target, updated_node.targets[0].target.value):
                return RemovalSentinel.REMOVE

            return updated_node

        def leave_AnnAssign(
                self, original_node: AnnAssign, updated_node: AnnAssign
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(original_node)

            if not isinstance(updated_node.target, Name) or isinstance(scope, ClassScope):
                # don't touch attributes (references not reliably detected)
                return updated_node

            if not self._is_referenced(original_node.target, updated_node.target.value):
                return RemovalSentinel.REMOVE

            return updated_node

        def leave_Import(
                self, original_node: Import, updated_node: Import
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            updated_imports = []

            for import_ in original_node.names:
                if import_.asname is None:
                    imported_name = import_.name.value if isinstance(import_.name, Name) else import_.name.attr.value
                else:
                    assert isinstance(import_.asname.name, Name)
                    imported_name = import_.asname.name.value

                if self._is_referenced(import_.name, imported_name):
                    updated_imports.append(import_)

            if len(updated_imports) > 0:
                updated_imports[-1] = updated_imports[-1].with_changes(comma=MaybeSentinel.DEFAULT)
                return updated_node.with_changes(names=updated_imports)

            return RemovalSentinel.REMOVE

        def leave_ImportFrom(
                self, original_node: ImportFrom, updated_node: ImportFrom
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            if isinstance(updated_node.names, ImportStar):
                # don't remove star imports
                return updated_node

            updated_imports = []

            for import_ in original_node.names:
                if import_.asname is None:
                    imported_name = import_.name.value if isinstance(import_.name, Name) else import_.name.attr.value
                else:
                    assert isinstance(import_.asname.name, Name)
                    imported_name = import_.asname.name.value

                if self._is_referenced(import_.name, imported_name):
                    updated_imports.append(import_)

            if len(updated_imports) > 0:
                updated_imports[-1] = updated_imports[-1].with_changes(comma=MaybeSentinel.DEFAULT)
                return updated_node.with_changes(names=updated_imports)

            return RemovalSentinel.REMOVE

        def _is_referenced(self, node: CSTNode, identifier: str, assignment=True) -> bool:
            if not assignment and self._analyses[ScopeAnalyzer].is_in_local_scope(node):
                scope = self._analyses[ScopeAnalyzer].get_scope_for_node(node)

                if identifier in scope.accesses:
                    # only remove unreferenced code in local scope
                    return True

                return False

            # fallback to assuming the code is referenced
            return True

    __config_name__ = 'remove_unreferenced_code'

