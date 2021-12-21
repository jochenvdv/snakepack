from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, FunctionDef, SimpleStatementSuite, IndentedBlock, Pass, BaseSmallStatement, Expr, Integer

from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemovePassTransformer(BatchablePythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._necessary_pass_stmts = set()

        def visit_SimpleStatementSuite(self, node: SimpleStatementSuite) -> Optional[bool]:
            if len(node.body) == 1 and isinstance(node.body[0], Pass):
                # single pass statement
                self._necessary_pass_stmts.add(node.body[0])

        def visit_IndentedBlock(self, node: IndentedBlock) -> Optional[bool]:
            if len(node.body) > 1 or len(node.body) == 0 or not isinstance(node.body[0], SimpleStatementLine):
                #  more than 1 statement line or it's a compound statement or no body
                return

            if len(node.body[0].body) == 1 and isinstance(node.body[0].body[0], Pass):
                #  single pass statement in the line
                self._necessary_pass_stmts.add(node.body[0].body[0])

        def leave_Pass(
                self, original_node: Pass, updated_node: Pass
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            if original_node in self._necessary_pass_stmts:
                #  convert to to literal zero expression ("0")
                return Expr(value=Integer(value='0'))
            else:
                return RemovalSentinel.REMOVE


    __config_name__ = 'remove_pass'
