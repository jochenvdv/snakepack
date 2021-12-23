from textwrap import dedent

from libcst import parse_module

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_semicolons import RemoveSemicolonsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveSemicolonsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RemoveSemicolonsTransformer

    def test_transform(self):
        input_content = dedent(
            """
            x = 5;
            foo();
            x=4;x=3;
            a:int=3;
            assert True;
            """
        )

        expected_output_content = dedent(
            """
            x = 5
            foo()
            x=4;x=3
            a:int=3
            assert True
            """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)