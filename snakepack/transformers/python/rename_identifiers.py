from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, SimpleStatementLine, BaseStatement, FlattenSentinel, \
    MaybeSentinel, Name, BaseExpression

from snakepack.transformers.python._base import PythonModuleTransformer


class NameRegistry:
    pass


class RemoveSemicolonsTransformer(PythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_Name(self, original_node: Name, updated_node: Name) -> BaseExpression:
            pass


    __config_name__ = 'rename_identifiers'
