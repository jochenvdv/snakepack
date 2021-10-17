from snakepack.assets import Asset
from snakepack.transformers import Transformer


class TransformerTest:
    class TestTransformer(Transformer):
        def transform(self, asset: Asset):
            pass

    def test_init(self):
        transformer = self.TestTransformer()
