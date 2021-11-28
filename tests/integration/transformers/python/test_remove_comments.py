from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveCommentsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    # this is a comment
                    x = 5 # this as well
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """

                    x = 5 
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveCommentsTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)