from __future__ import annotations

from typing import Mapping, Type, Union

from libcst import CSTTransformer, CSTNode, FunctionDef, ClassDef, Name, Attribute, Assign, AnnAssign, CSTNodeT, \
    RemovalSentinel, FlattenSentinel

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets import AssetContent, AssetGroup
from snakepack.assets.python import PythonModuleCst, PythonModule, Python
from snakepack.config.options import Options
from snakepack.transformers import Transformer


class PythonModuleTransformer(Transformer):
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


class BatchablePythonModuleTransformer(PythonModuleTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_cst_transformer(self, subject, options, analyses, transformer) -> CSTTransformer:
        return self._CstTransformer(
            subject=subject,
            options=options,
            analyses=analyses,
            transformer=transformer
        )


class BatchPythonModuleTransformer(PythonModuleTransformer):
    def __init__(self, transformers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transformers = transformers

    def transform(
            self,
            analyses: Mapping[Type[Analyzer], Analyzer.Analysis],
            subject: Union[PythonModule, AssetGroup[Python]]
    ) -> Union[PythonModule, AssetGroup[Python]]:
        if isinstance(subject, PythonModule):
            cst_transformers = [
                transformer.create_cst_transformer(subject, self._options, analyses, self)
                for transformer in self._transformers
            ]
            transformer = self._CstTransformer(
                subject=subject,
                options=self._options,
                analyses=analyses,
                transformer=self,
                transformers=cst_transformers
            )
            subject.content = PythonModuleCst(cst=subject.content.cst.visit(transformer))

        return subject

    class _CstTransformer(PythonModuleTransformer._CstTransformer):
        def __init__(self, transformers, *args, **kwargs):
            self._transformers = transformers

        def on_visit(self, node: CSTNode) -> bool:
            return_value = True

            for transformer in self._transformers:
                visit_func = getattr(transformer, f"visit_{type(node).__name__}", None)

                if visit_func is not None:
                    transformer_return_value = visit_func(node)
                else:
                    transformer_return_value = True

                if not return_value and transformer_return_value:
                    return_value = True

            return return_value

        def on_leave(
                self, original_node: CSTNodeT, updated_node: CSTNodeT
        ) -> Union[CSTNodeT, RemovalSentinel, FlattenSentinel[CSTNodeT]]:
            for transformer in self._transformers:
                leave_func = getattr(transformer, f"leave_{type(original_node).__name__}", None)

                if leave_func is not None:
                    updated_node = leave_func(original_node, updated_node)

                    if updated_node is RemovalSentinel.REMOVE:
                        break

            return updated_node