from textwrap import dedent
from unittest.mock import MagicMock

from libcst import parse_module

from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_unreferenced_code import RemoveUnreferencedCodeTransformer
from snakepack.transformers.python.rename_identifiers import RenameIdentifiersTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveUnreferencedCodeTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
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
                    """
                )
            )
        )
        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
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
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveUnreferencedCodeTransformer(global_options=global_options)

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