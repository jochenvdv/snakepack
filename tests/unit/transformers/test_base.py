from snakepack.assets import Asset
from snakepack.config.model import GlobalOptions
from snakepack.transformers import Transformer


class TransformerTest:
    class TestTransformer(Transformer):
        def transform(self, asset: Asset):
            pass

        __config_name__ = 'test_transformer'

    def test_init(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        transformer = self.TestTransformer(global_options=global_options)
