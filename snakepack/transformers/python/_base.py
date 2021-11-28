from __future__ import annotations

from typing import Mapping, Type, Union

from libcst import CSTTransformer, CSTNode, FunctionDef, ClassDef, Name, Attribute, Assign, AnnAssign

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets import AssetContent, AssetGroup
from snakepack.assets.python import PythonModuleCst, PythonModule, Python
from snakepack.config.options import Options
from snakepack.transformers import Transformer


class PythonModuleTransformer(Transformer):
    REQUIRED_ANALYZERS = Transformer.REQUIRED_ANALYZERS + [
        ScopeAnalyzer
    ]

    SUPPORTS_FINEGRAINED_EXCLUSIONS = False

    def transform(
            self,
            analyses: Mapping[Type[Analyzer], Analyzer.Analysis],
            subject: Union[PythonModule, AssetGroup[Python]]
    ) -> Union[PythonModule, AssetGroup[Python]]:
        if isinstance(subject, PythonModule):
            transformer = self._CstTransformer(subject=subject, options=self._options, analyses=analyses, transformer=self)
            subject.content = PythonModuleCst(cst=subject.content.cst.visit(transformer))

        return subject

    class _CstTransformer(CSTTransformer):
        def __init__(
                self,
                subject: PythonModule,
                options: Options,
                analyses: Mapping[Type[Analyzer],Analyzer.Analysis],
                transformer: PythonModuleTransformer
        ):
            super().__init__()
            self._subject = subject
            self._options = options
            self._analyses = analyses
            self._transformer = transformer

        def on_visit(self, node: CSTNode) -> bool:
            if (
                    self._transformer.SUPPORTS_FINEGRAINED_EXCLUSIONS
                    and len(self._options.excludes) > 0
                    and isinstance(node, (ClassDef, FunctionDef))
            ):
                names = self._analyses[ScopeAnalyzer].get_fully_qualified_names(self._subject, node)

                if any(map(lambda x: x in names, self._options.excludes)):
                    return False

            return super().on_visit(node)
