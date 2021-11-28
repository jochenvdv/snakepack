from typing import Mapping

from snakepack.assets import Asset
from snakepack.assets._base import AssetContentSource
from snakepack.config.model import GlobalOptions
from snakepack.loaders import Loader


class LoaderTest:
    class TestLoader(Loader):
        def load(self) -> Mapping[Asset, AssetContentSource]:
            return {}

    def test_init(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        loader = self.TestLoader(global_options=global_options)

