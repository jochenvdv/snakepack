from textwrap import dedent

from libcst import parse_module

from snakepack.analyzers.python.literals import LiteralDuplicationAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.hoist_literals import HoistLiteralsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemovePassTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    foo('some_long_string', x['some_long_string'])
                    y = 'some_long_string'
                    foo('s', x['s'])
                    foo('r', 'r', 'r')
                    x = 'assigned'
                    foo('assigned', 'assigned', 'assigned')
                    """
                )
            )
        )

        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    a='some_long_string'; c='r'
                    foo(a, x[a])
                    y = a
                    foo('s', x['s'])
                    foo(c, c, c)
                    x = 'assigned'
                    foo(x, x, x)
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = HoistLiteralsTransformer(global_options=global_options)

        self._test_transformation(
            transformer=transformer,
            input=input_content,
            expected_output=expected_output_content,
            analyzers=[LiteralDuplicationAnalyzer()]
        )
