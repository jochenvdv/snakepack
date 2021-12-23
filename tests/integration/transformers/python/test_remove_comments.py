from textwrap import dedent

from libcst import parse_module

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python._base import PythonModuleTransformer
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveCommentsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RemoveCommentsTransformer

    def test_transform(self):
        input_content = dedent(
            """
            # this is a comment
            x = 5 # this as well
            """
        )

        expected_output_content = dedent(
            """
                
            x = 5 
            """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)
