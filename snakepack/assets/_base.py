from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TypeVar, Protocol, Optional, Union, Generic, Type, Any


class AssetType(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @classmethod
    def create(cls, name: str):
        asset_type = type(name, (cls,), {})
        return asset_type


T = TypeVar('T', bound=AssetType)


class Asset(Generic[T], ABC):
    def __init__(self, content: AssetContent[Asset[T]]):
        self._content = content

    @property
    def content(self) -> AssetContent[Asset[T]]:
        return self._content

    @content.setter
    def content(self, content: AssetContent[Asset[T]]):
        self._content = content

    @classmethod
    def from_string(cls, string: str) -> Asset[T]:
        return cls(content=StringAssetContent(string))


class AssetGroup(Generic[T]):
    @property
    @abstractmethod
    def assets(self):
        raise NotImplementedError


U = TypeVar('U', bound=Asset)


class AssetContent(Generic[U], ABC):
    def to_string(self) -> StringAssetContent:
        return StringAssetContent(str(self))

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_string(cls, string_content) -> AssetContent:
        raise NotImplementedError


class StringAssetContent(AssetContent[U]):
    def __init__(self, string: str):
        self._string = string

    def __str__(self) -> str:
        return self._string

    @classmethod
    def from_string(cls, string_content) -> StringAssetContent:
        return string_content


class AssetContentSource(ABC):
    @abstractmethod
    def load(self) -> StringAssetContent:
        raise NotImplementedError


class RuntimeContentSource(AssetContentSource):
    def __init__(self, content: AssetContent):
        self._content = content

    def load(self) -> StringAssetContent:
        return self._content.to_string()


class FileContentSource(AssetContentSource):
    def __init__(self, path):
        self._path = path

    def load(self) -> StringAssetContent:
        with open(self._path) as f:
            return StringAssetContent(f.read())


class AssetContentCache:
    def __init__(self, content_or_source: Union[AssetContentSource, AssetContent]):
        if isinstance(content_or_source, AssetContentSource):
            self._content_source = content_or_source
            self._cached_content = None
        else:
            self._cached_content = content_or_source
            self._content_source = None

    def __getattr__(self, attr) -> Any:
        self._ensure_content_loaded()
        return getattr(self._cached_content, attr)

    def __getitem__(self, item: Type[AssetContent]) -> AssetContentCache:
        self._ensure_content_loaded()

        if not isinstance(self._cached_content, item):
            self._cached_content = item.from_string(self._cached_content.to_string())

        return self

    def __str__(self) -> str:
        self._ensure_content_loaded()
        return str(self._cached_content)

    def _ensure_content_loaded(self):
        if self._cached_content is None:
            self._cached_content = self._content_source.load()
