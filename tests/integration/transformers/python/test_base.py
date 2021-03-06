from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python import RemoveAnnotationsTransformer, RemoveAssertionsTransformer, \
    RemoveCommentsTransformer
from snakepack.transformers.python._base import BatchPythonModuleTransformer, PythonModuleTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class BatchPythonModuleTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    def test_transform(self):
        input_content = dedent(
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

        expected_output_content = dedent(
            """
            x: int = 5
            def func(param: str) -> bool: pass
            class Foo:
                attr: str
                anattr: int = 7
            x=5; 
            
            x = 5 
            """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)

    def _create_transformer(self, options=None) -> PythonModuleTransformer:
        global_options = GlobalOptions()

        if options is None:
            options = BatchPythonModuleTransformer.Options()

        transformers = [
            RemoveAssertionsTransformer(global_options=global_options, options=options),
            RemoveCommentsTransformer(global_options=global_options, options=options)
        ]
        batch_transformer = BatchPythonModuleTransformer(transformers=transformers, global_options=global_options)

        return batch_transformer