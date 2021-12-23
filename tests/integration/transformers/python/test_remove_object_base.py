from textwrap import dedent

from libcst import parse_module

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_object_base import RemoveObjectBaseTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveObjectBaseTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RemoveObjectBaseTransformer

    def test_transform(self):
        input_content = dedent(
            """
            class Test(object): pass
            class EdgeCase(Test): pass
            class Another(): pass
            class Final: pass
            """
        )

        expected_output_content = dedent(
            """
            class Test: pass
            class EdgeCase(Test): pass
            class Another: pass
            class Final: pass
            """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)