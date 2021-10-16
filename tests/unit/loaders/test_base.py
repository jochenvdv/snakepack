from typing import Mapping

from snakepack.assets import Asset
from snakepack.assets._base import AssetContentSource
from snakepack.loaders import Loader


class LoaderTest:
    class TestLoader(Loader):
        def load(self) -> Mapping[Asset, AssetContentSource]:
            return {}

    def test_init(self):
        loader = self.TestLoader()

