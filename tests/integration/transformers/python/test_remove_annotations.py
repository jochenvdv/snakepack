from textwrap import dedent
from typing import Iterable

from libcst import parse_module

from analyzers import Analyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_annotations import RemoveAnnotationsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveAnnotationsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RemoveAnnotationsTransformer

    def test_transform(self):
        input_content = dedent(
                """
                x: int = 5
                def func(param: str) -> bool: pass
                class Foo:
                    attr: str
                    anattr: int = 7
                if0:del0#
                """
        )

        expected_output_content = dedent(
                """
                x = 5
                def func(param): pass
                class Foo:
                    attr: str
                    anattr: int = 7
                if0:del0#
                """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)

    def test_transform_remove_in_class_definitions_true(self):
        input_content = dedent(
            """
            x: int = 5
            def func(param: str) -> bool: pass
            class Foo:
                attr: str
                anattr: int = 7
            if0:del0#
            """
        )

        expected_output_content = dedent(
            """
            x = 5
            def func(param): pass
            class Foo:
                attr: str
                anattr = 7
            if0:del0#
            """
        )

        self._test_transformation(
            input=input_content,
            expected_output=expected_output_content,
            options=RemoveAnnotationsTransformer.Options(
                remove_in_class_definitions=True
            )
        )

    def _create_analyzers(self) -> Iterable[Analyzer]:
        return [
            ScopeAnalyzer(),
        ]