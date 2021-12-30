from pathlib import Path

from snakepack.assets import AssetType, AssetContent
from snakepack.assets.generic import GenericAsset, StaticFile


class GenericAssetTest:
    def test_generic_asset_type(self):
        assert issubclass(GenericAsset, AssetType)


class StaticFileTest:
    def test_init(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        module = StaticFile(name='some_file', target_path=Path('some_file.txt'), content=content, source=None)

        assert module.content is content
