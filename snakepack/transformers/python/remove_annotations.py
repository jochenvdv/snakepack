from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, Annotation, FunctionDef, BaseStatement, FlattenSentinel, \
    Param, MaybeSentinel, AnnAssign, BaseSmallStatement, AssignTarget, Assign, Name
from libcst.metadata import ClassScope

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveAnnotationsTransformer(PythonModuleTransformer):
    REQUIRED_ANALYZERS = PythonModuleTransformer.REQUIRED_ANALYZERS + [
        ScopeAnalyzer
    ]

    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_FunctionDef(
                self, original_node: FunctionDef, updated_node: FunctionDef
        ) -> Union[BaseStatement, RemovalSentinel]:
            return updated_node.with_changes(returns=None)

        def leave_Param(self, original_node: Param, updated_node: Param) -> Union[Param, MaybeSentinel, RemovalSentinel]:
            return updated_node.with_changes(annotation=None)

        def leave_AnnAssign(
                self, original_node: AnnAssign, updated_node: AnnAssign
        ) -> Union[BaseSmallStatement, RemovalSentinel]:
            if updated_node.value is None:
                # don't remove type annotation because variable is not initialized
                return updated_node

            scope = self._analyses[ScopeAnalyzer].get_scope_for_node(original_node)

            if not self._options.remove_in_class_definitions and isinstance(scope, ClassScope):
                # don't remove annotation in class definition
                return updated_node

            target = AssignTarget(target=updated_node.target)
            updated_value = updated_node.value
            updated_node = Assign(targets=[target], value=updated_value, semicolon=updated_node.semicolon)

            return updated_node

    class Options(PythonModuleTransformer.Options):
        remove_in_class_definitions: bool = False

    __config_name__ = 'remove_annotations'