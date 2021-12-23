from textwrap import dedent

from libcst import parse_module

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_parameter_separators import RemoveParameterSeparatorsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveParameterSeparatorsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RemoveParameterSeparatorsTransformer

    def test_transform(self):
        input_content = dedent(
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

        expected_output_content = dedent(
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

        self._test_transformation(input=input_content, expected_output=expected_output_content)