from pathlib import Path
from typing import Iterable

from snakepack.assets import (
    AssetType,
    Asset,
    AssetContent,
    StringAssetContent, AssetGroup, AssetContentSource, FileContentSource, AssetContentCache
)
from snakepack.assets._base import T


class AssetTypeTest:
    def test_create(self):
        Test = AssetType.create('Test')

        assert issubclass(Test, AssetType)


class AssetTest:
    class TestAsset(Asset):
        pass

    def test_init(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        asset = self.TestAsset(name='test', target_path=Path('./test.txt'), content=content, source=None)

        assert asset.name == 'test'
        assert asset.target_path == Path('./test.txt')
        assert asset.content is content
        assert asset.source is None

    def test_content_setter(self, mocker):
        orig_content = mocker.MagicMock(spec=AssetContent)
        asset = self.TestAsset(name='test', target_path=Path('./test.py'), content=orig_content, source=None)

        new_content = mocker.MagicMock(spec=AssetContent)
        asset.content = new_content

        assert asset.content is new_content

    def test_from_string(self, mocker):
        asset = self.TestAsset.from_string(name='test', target_path=Path('./test.py'), content='test')

        assert isinstance(asset.content, StringAssetContent)
        assert str(asset.content) == 'test'


class AssetContentTest:
    class TestAssetContent(AssetContent):
        def __init__(self, string):
            self._string = string

        def __str__(self):
            return self._string

        @classmethod
        def from_string(cls, string_content):
            return AssetContentTest.TestAssetContent('test')

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

        @property
        def deep_assets(self) -> Iterable[Asset[T]]:
            return self._assets

        @property
        def subgroups(self) -> Iterable[AssetGroup[T]]:
            return []

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


class AssetContentCacheTest:
    class TestAssetContentA(AssetContent):
        def __str__(self):
            return 'A'

        @classmethod
        def from_string(cls, string_content):
            return cls()

    class TestAssetContentB(AssetContent):
        def __str__(self):
            return 'B'

        @classmethod
        def from_string(cls, string_content):
            return cls()

    def test_init_with_source(self, mocker):
        content_source = mocker.MagicMock(spec=AssetContentSource)
        cache = AssetContentCache(content_or_source=content_source)

    def test_init_with_content(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        cache = AssetContentCache(content_or_source=content)

    def test_getattr(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        content.test = 'test'
        cache = AssetContentCache(content_or_source=content)

        assert cache.test == 'test'

    def test_getattr_cache_miss(self, mocker):
        content_source = mocker.MagicMock(spec=AssetContentSource)
        content = mocker.MagicMock(spec=AssetContent)
        content.test = 'test'
        content_source.load.return_value = content
        cache = AssetContentCache(content_or_source=content_source)

        assert cache.test == 'test'

    def test_getitem(self, mocker):
        content = self.TestAssetContentA()
        cache = AssetContentCache(content_or_source=content)

        casted_cache = cache[self.TestAssetContentB]

        assert casted_cache == cache
        assert str(casted_cache) == 'B'

    def test_getitem_cache_miss(self, mocker):
        content_source = mocker.MagicMock(spec=AssetContentSource)
        content_source.load.return_value = self.TestAssetContentA()
        cache = AssetContentCache(content_or_source=content_source)

        casted_cache = cache[self.TestAssetContentB]

        assert casted_cache == cache
        assert str(casted_cache) == 'B'
