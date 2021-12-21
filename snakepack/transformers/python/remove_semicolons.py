from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel

from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveSemicolonsTransformer(BatchablePythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_SimpleStatementLine(
                self, original_node: SimpleStatementLine, updated_node: SimpleStatementLine
        ) -> Union[BaseStatement, FlattenSentinel[BaseStatement], RemovalSentinel]:
            updated_statements = []
            num_statements = len(original_node.body)

            for index, statement in enumerate(original_node.body):
                if index == num_statements - 1:  # last statement, semicolon not required
                    updated_statements.append(statement.with_changes(semicolon=MaybeSentinel.DEFAULT))
                else:
                    updated_statements.append(statement)

            return updated_node.with_changes(body=updated_statements)


    __config_name__ = 'remove_semicolons'
