from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, Annotation, FunctionDef, BaseStatement, FlattenSentinel, \
    Param, MaybeSentinel, AnnAssign, BaseSmallStatement, AssignTarget, Assign, Name

from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveAnnotationsTransformer(BatchablePythonModuleTransformer):
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

            target = AssignTarget(target=updated_node.target)
            updated_value = updated_node.value
            updated_node = Assign(targets=[target], value=updated_value, semicolon=updated_node.semicolon)

            return updated_node

    __config_name__ = 'remove_annotations'