from textwrap import dedent

from libcst import parse_module

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_assertions import RemoveAssertionsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveAssertionsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RemoveAssertionsTransformer

    def test_transform(self):
        input_content = dedent(
            """
            assert False, 'not ok'
            x=5; assert True, 'bad'
            """
        )

        expected_output_content = dedent(
            """
            x=5; 
            """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)