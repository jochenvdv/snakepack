from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config import GlobalOptions
from snakepack.transformers.python.remove_literal_statements import RemoveLiteralStatementsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RemoveLiteralStatementsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = PythonModuleCst(
            cst=parse_module(
                dedent(
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
            )
        )

        expected_output_content = PythonModuleCst(
            cst=parse_module(
                dedent(
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
            )
        )
        global_options = GlobalOptions()
        transformer = RemoveLiteralStatementsTransformer(global_options=global_options)

        self._test_transformation(transformer=transformer, input=input_content, expected_output=expected_output_content)