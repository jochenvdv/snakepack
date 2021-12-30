from textwrap import dedent
from typing import Iterable
from unittest.mock import MagicMock

from libcst import parse_module

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_unreferenced_code import RemoveUnreferencedCodeTransformer
from snakepack.transformers.python.rename_identifiers import RenameIdentifiersTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveUnreferencedCodeTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RemoveUnreferencedCodeTransformer

    def test_transform(self):
        input_content = dedent(
            """
            def imported(a, b):
                x = 5
            not_used = 'indeed'
            class UsedInternally:
                x = 5
            def _internal():
                pass
            def _used(obj):
                pass
            _used(UsedInternally())
            class _NotUsed:
                pass
            useless: int = 400
            useful: int = 200
            assert useful
            import bar
            bar.foo()
            import nope
            import something as other
            other.ok()
            import something as unused
            import a as b, c as d, e as f
            print(b, f)
            from ... import u as v, x as y, z as zz
            from module import *
            from module2 import func, var
            print(var, zz)
            """
        )

        expected_output_content = dedent(
                    """
                    def imported(a, b):
                        pass
                    class UsedInternally:
                        x = 5
                    def _used(obj):
                        pass
                    _used(UsedInternally())
                    useful: int = 200
                    assert useful
                    import bar
                    bar.foo()
                    import something as other
                    other.ok()
                    import a as b, e as f
                    print(b, f)
                    from ... import z as zz
                    from module import *
                    from module2 import var
                    print(var, zz)
                    """
                )

        self._test_transformation(input=input_content, expected_output=expected_output_content)

    def _create_analyzers(self) -> Iterable[Analyzer]:
        def _get_importing_modules(module, identifier):
            if identifier == 'imported':
                return [
                    MagicMock()
                ]

            return []

        import_graph_analysis = MagicMock(spec=ImportGraphAnalyzer.Analysis)
        import_graph_analysis.get_importing_modules.side_effect = _get_importing_modules
        import_graph_analyzer = MagicMock(spec=ImportGraphAnalyzer)
        import_graph_analyzer.analyse_assets.return_value = import_graph_analysis

        return [
            ScopeAnalyzer(),
            import_graph_analyzer
        ]