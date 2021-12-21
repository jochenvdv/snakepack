from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python import RemoveAnnotationsTransformer, RemoveAssertionsTransformer, \
    RemoveCommentsTransformer
from snakepack.transformers.python._base import BatchPythonModuleTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class BatchPythonModuleTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
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
                    assert False, 'not ok'
                    x=5; assert True, 'bad'
                    # this is a comment
                    x = 5 # this as well
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
                    x=5; 
                    
                    x = 5 
                    """
                )
            )
        )
        global_options = GlobalOptions()
        transformers = [
            RemoveAnnotationsTransformer(global_options=global_options),
            RemoveAssertionsTransformer(global_options=global_options),
            RemoveCommentsTransformer(global_options=global_options)
        ]
        batch_transformer = BatchPythonModuleTransformer(transformers=transformers, global_options=global_options)

        self._test_transformation(
            transformer=batch_transformer,
            input=input_content,
            expected_output=expected_output_content,
            analyzers=[]
        )