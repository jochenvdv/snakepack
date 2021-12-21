from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel, Assert, FlattenSentinel, BaseSmallStatement

from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveAssertionsTransformer(BatchablePythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_Assert(
            self, original_node: Assert, updated_node: Assert
        ) -> Union[BaseSmallStatement, FlattenSentinel[BaseSmallStatement], RemovalSentinel]:
            return RemovalSentinel.REMOVE


    __config_name__ = 'remove_assertions'
