import pytest
from libcst import Module

from snakepack.assets import Asset
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.remove_comments import RemoveCommentsTransformer


class RemoveCommentsTransformerTest:
    def test_config_name(self):
        assert RemoveCommentsTransformer.__config_name__ == 'remove_comments'

    def test_init(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        transformer = RemoveCommentsTransformer(global_options=global_options)

    @pytest.mark.skip
    def test_transform(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        transformer = RemoveCommentsTransformer(global_options=global_options)

        content = mocker.MagicMock(spec=PythonModuleCst)
        orig_cst = mocker.MagicMock(spec=Module)
        changed_cst = mocker.MagicMock(spec=Module)
        content.cst = orig_cst
        orig_cst.visit.return_value = changed_cst

        assert transformer.transform(content).cst is changed_cst
