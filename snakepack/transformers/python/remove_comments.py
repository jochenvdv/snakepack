from typing import Optional, Union

from libcst import CSTTransformer, Comment, RemovalSentinel

from snakepack.assets import Asset
from snakepack.assets.python import PythonModuleCst, PythonModule
from snakepack.transformers import Transformer


class RemoveCommentsTransformer(Transformer):
    def __init__(self):
        self._transformer = self._CstTransformer()

    def transform(self, asset: PythonModule) -> PythonModuleCst:
        return PythonModuleCst(cst=asset.content.cst.visit(self._transformer))

    class _CstTransformer(CSTTransformer):
        def leave_Comment(
            self, original_node: Comment, updated_node: Comment
        ) -> Union[Comment, RemovalSentinel]:
            return RemovalSentinel.REMOVE

