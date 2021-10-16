from snakepack.assets import (
    AssetType,
    Asset,
    AssetContent,
    StringAssetContent, AssetGroup
)
from snakepack.assets._base import AssetContentSource, FileContentSource


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


class AssetContentSourceTest:
    class TestAssetContentSource(AssetContentSource):
        def load(self) -> StringAssetContent:
            return StringAssetContent('test')

    def test_init(self):
        source = self.TestAssetContentSource()


class RuntimeContentSource(AssetContentSource):
    def test_init(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        source = RuntimeContentSource(content=content)

    def test_load(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        string_content = mocker.MagicMock(spec=StringAssetContent)
        content.to_string.return_value = string_content

        source = RuntimeContentSource(content=content)
        loaded_content = source.load()

        assert loaded_content is string_content
        content.to_string.assert_called_once()


class FileContentSourceTest:
    def test_init(self):
        source = FileContentSource(path='test.py')

    def test_load(self, fs):
        fs.create_file('test.py', contents='test=True')

        source = FileContentSource(path='test.py')
        content = source.load()

        assert isinstance(content, StringAssetContent)
        assert str(content) == 'test=True'
