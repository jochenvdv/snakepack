from snakepack.assets import Asset
from snakepack.transformers import Transformer


class TransformerTest:
    class TestTransformer(Transformer):
        def transform(self, asset: Asset):
            pass

        __config_name__ = 'test_transformer'

    def test_init(self):
        transformer = self.TestTransformer()
