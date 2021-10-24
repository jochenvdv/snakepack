from libcst import CSTTransformer

from snakepack.assets import AssetContent
from snakepack.assets.python import PythonModuleCst
from snakepack.transformers import Transformer


class PythonModuleCstTransformer(Transformer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transformer = self._CstTransformer()

    def transform(self, content: PythonModuleCst) -> PythonModuleCst:
        return PythonModuleCst(cst=content.cst.visit(self._transformer))

    class _CstTransformer(CSTTransformer):
        NotImplemented
