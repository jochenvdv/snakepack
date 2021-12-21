from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel

from snakepack.transformers.python._base import PythonModuleTransformer, BatchablePythonModuleTransformer


class RemoveCommentsTransformer(BatchablePythonModuleTransformer):
    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def leave_Comment(self, original_node: Comment, updated_node: Comment) -> Union[Comment, RemovalSentinel]:
            return RemovalSentinel.REMOVE

    __config_name__ = 'remove_comments'