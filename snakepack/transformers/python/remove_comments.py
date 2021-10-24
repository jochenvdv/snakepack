from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel

from snakepack.transformers.python._base import PythonModuleCstTransformer


class RemoveCommentsTransformer(PythonModuleCstTransformer):
    class _CstTransformer(CSTTransformer):
        def leave_Comment(self, original_node: Comment, updated_node: Comment) -> Union[Comment, RemovalSentinel]:
            return RemovalSentinel.REMOVE

    __config_name__ = 'remove_comments'