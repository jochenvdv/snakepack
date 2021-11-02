from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.remove_annotations import RemoveAnnotationsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveAnnotationsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x: int = 5
                    def func(param: str) -> bool: pass
                    class Foo:
                        attr: str
                        anattr: int = 7
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x = 5
                    def func(param): pass
                    class Foo:
                        attr = None
                        anattr = 7
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveAnnotationsTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)