from textwrap import dedent

from libcst import parse_module

from snakepack.assets.python import PythonModule, PythonModuleCst
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer


class RemoveCommentsTransformerIntegrationTest:
    def test_transform(self):
        orig_code = dedent(
            """
            # this is a comment
            x = 5 # this as well
            """
        )
        asset = PythonModule(
            full_name='test',
            content=PythonModuleCst(
                cst=parse_module(orig_code)
            )
        )

        transformer = RemoveCommentsTransformer()
        new_content = transformer.transform(asset)

        assert str(new_content) == dedent(
            """
            
            x = 5 
            """
        )