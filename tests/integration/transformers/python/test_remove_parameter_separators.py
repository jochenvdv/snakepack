from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.remove_parameter_separators import RemoveParameterSeparatorsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveParameterSeparatorsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    def func(a, b, /, c, d, *args, e, f, **kwargs): pass
                    def func(a, b, /, c, d, *, e, f, **kwargs): pass
                    def func(a, b, /, c, d, e, f, **kwargs): pass
                    def func(a, b, c, d, *, e, f, **kwargs): pass
                    _ = lambda a, b, /, c, d, *args, e, f, **kwargs: None
                    _ = lambda a, b, /, c, d, *, e, f, **kwargs: None
                    _ = lambda a, b, /, c, d, e, f, **kwargs: None
                    _ = lambda a, b, c, d, *, e, f, **kwargs: None
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    def func(a, b, c, d, *args, e, f, **kwargs): pass
                    def func(a, b, c, d, e, f, **kwargs): pass
                    def func(a, b, c, d, e, f, **kwargs): pass
                    def func(a, b, c, d, e, f, **kwargs): pass
                    _ = lambda a, b, c, d, *args, e, f, **kwargs: None
                    _ = lambda a, b, c, d, e, f, **kwargs: None
                    _ = lambda a, b, c, d, e, f, **kwargs: None
                    _ = lambda a, b, c, d, e, f, **kwargs: None
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveParameterSeparatorsTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)