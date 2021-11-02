from typing import Mapping, Type, Union

from libcst import CSTTransformer

from snakepack.analyzers import Analyzer
from snakepack.assets import AssetContent, AssetGroup
from snakepack.assets.python import PythonModuleCst, PythonModule, Python
from snakepack.config import Options
from snakepack.transformers import Transformer


class PythonModuleTransformer(Transformer):
    def transform(
            self,
            analyses: Mapping[Type[Analyzer], Analyzer.Analysis],
            subject: Union[PythonModule, AssetGroup[Python]]
    ) -> Union[PythonModule, AssetGroup[Python]]:
        if isinstance(subject, PythonModule):
            transformer = self._CstTransformer(options=self._options, analyses=analyses)
            subject.content = PythonModuleCst(cst=subject.content.cst.visit(transformer))

        return subject

    class _CstTransformer(CSTTransformer):
        def __init__(self, options: Options, analyses: Mapping[Type[Analyzer], Analyzer.Analysis]):
            super().__init__()
            self._options = options
            self._analyses = analyses
