from libcst import Module

from snakepack.assets import Asset
from snakepack.assets.python import PythonModuleCst
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer


class RemoveCommentsTransformerTest:
    def test_init(self):
        transformer = RemoveCommentsTransformer()

    def test_transform(self, mocker):
        transformer = RemoveCommentsTransformer()

        asset = mocker.MagicMock(spec=Asset)
        content = mocker.MagicMock(spec=PythonModuleCst)
        orig_cst = mocker.MagicMock(spec=Module)
        changed_cst = mocker.MagicMock(spec=Module)
        content.cst = orig_cst
        asset.content = content
        orig_cst.visit.return_value = changed_cst

        assert transformer.transform(asset).cst is changed_cst
