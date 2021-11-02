from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.remove_object_base import RemoveObjectBaseTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveObjectBaseTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    class Test(object): pass
                    class EdgeCase(Test): pass
                    class Another(): pass
                    class Final: pass
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    class Test: pass
                    class EdgeCase(Test): pass
                    class Another: pass
                    class Final: pass
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveObjectBaseTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)