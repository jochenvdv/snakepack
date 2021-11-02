from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.remove_semicolons import RemoveSemicolonsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveSemicolonsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x = 5;
                    foo();
                    x=4;x=3;
                    a:int=3;
                    assert True;
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x = 5
                    foo()
                    x=4;x=3
                    a:int=3
                    assert True
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveSemicolonsTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)