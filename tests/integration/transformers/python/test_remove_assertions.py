from textwrap import dedent

from libcst import parse_module

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_assertions import RemoveAssertionsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveAssertionsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
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

        self._test_transformation(
            transformer=transformer,
            input=input_content,
            expected_output=expected_output_content,
            analyzers=[ScopeAnalyzer()]
        )