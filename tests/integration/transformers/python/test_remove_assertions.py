from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.remove_assertions import RemoveAssertionsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveAssertionsPythonModuleCstTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    assert False, 'not ok'
                    x=5; assert True, 'bad'
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x=5; 
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveAssertionsTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)