from snakepack.assets import (
    AssetType,
    Asset,
    AssetContent,
    StringAssetContent, AssetGroup
)


class AssetTypeTest:
    def test_create(self):
        Test = AssetType.create('Test')

        assert issubclass(Test, AssetType)


class AssetTest:
    class TestAsset(Asset):
        pass

    def test_init(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        asset = self.TestAsset(content=content)

        assert asset.content is content

    def test_content_setter(self, mocker):
        orig_content = mocker.MagicMock(spec=AssetContent)
        asset = self.TestAsset(content=orig_content)

        new_content = mocker.MagicMock(spec=AssetContent)
        asset.content = new_content

        assert asset.content is new_content

    def test_from_string(self, mocker):
        asset = self.TestAsset.from_string('test')

        assert isinstance(asset.content, StringAssetContent)
        assert str(asset.content) == 'test'


class AssetContentTest:
    class TestAssetContent(AssetContent):
        def __init__(self, string):
            self._string = string

        def __str__(self):
            return self._string

    def test_init(self):
        content = self.TestAssetContent('test')

    def test_to_string(self):
        content = self.TestAssetContent('test')
        string_content = content.to_string()

        assert isinstance(string_content, StringAssetContent)
        assert str(string_content) == 'test'


class StringAssetContentTest:
    def test_init(self):
        content = StringAssetContent('test')

        assert str(content) == 'test'


class AssetGroupTest:
    class TestAssetGroup(AssetGroup):
        def __init__(self, assets):
            self._assets = assets

        @property
        def assets(self):
            return self._assets

    def test_init(self):
        group = self.TestAssetGroup(assets=[])
