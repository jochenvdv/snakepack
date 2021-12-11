from textwrap import dedent
from unittest.mock import MagicMock

from libcst import parse_module

from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.rename_identifiers import RenameIdentifiersTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RenameIdentifiersTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    x = 5;
                    def foo(attr, anattr):
                        pass
                    def bar(attr, anattr):
                        return b(attr, anattr)
                    class Class(object):
                        attr = 'foo'
                    foo(x);
                    y = 6
                    a = x + y
                    Class.attr = 'bar'
                    def imported(a, b, c):
                        o = True
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    a = 5;
                    def b(a, b):
                        pass
                    def c(a, c):
                        return b(a, c)
                    class d(object):
                        attr = 'foo'
                    b(a);
                    e = 6
                    f = a + e
                    d.attr = 'bar'
                    def imported(a, b, c):
                        d = True
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RenameIdentifiersTransformer(global_options=global_options)

        def _get_importing_modules(module, identifier):
            if identifier == 'imported':
                return [
                    MagicMock()
                ]

            return []

        import_graph_analysis = MagicMock(spec=ImportGraphAnalyzer.Analysis)
        import_graph_analysis.get_importing_modules.side_effect = _get_importing_modules
        import_graph_analyzer = MagicMock(spec=ImportGraphAnalyzer)
        import_graph_analyzer.analyse.return_value = import_graph_analysis

        self._test_transformation(
            transformer=transformer,
            input=input_content,
            expected_output=expected_output_content,
            analyzers=[
                ScopeAnalyzer(),
                import_graph_analyzer
            ]
        )