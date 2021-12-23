from textwrap import dedent

from libcst import parse_module

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_literal_statements import RemoveLiteralStatementsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveLiteralStatementsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RemoveLiteralStatementsTransformer

    def test_transform(self):
        input_content = dedent(
            """
            def foo():
                \"\"\" foo \"\"\"
                0
                def nested():
                    400
                    200
                pass
            
            if True:
                2; print('ok')
            
            try: 0
            except: 1; print('ok')
            """
        )

        expected_output_content = dedent(
            """
            def foo():
                def nested():
                    0
                pass
                
            if True:
                print('ok')
                
            try: 0
            except: print('ok')
            """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)