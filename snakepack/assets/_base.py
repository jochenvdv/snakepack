from __future__ import annotations

from abc import abstractmethod, ABC
from pathlib import Path
from typing import TypeVar, Protocol, Optional, Union, Generic, Type, Any, Iterable

from snakepack.config.options import Selectable


class AssetType(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @classmethod
    def create(cls, name: str):
        asset_type = type(name, (cls,), {})
        return asset_type


T = TypeVar('T', bound=AssetType)


class Asset(Generic[T], Selectable, ABC):
    def __init__(self, content: AssetContent[Asset[T]], source: AssetContentSource):
        self._content = content
        self._source = source

    @property
    def content(self) -> AssetContent[Asset[T]]:
        return self._content

    @content.setter
    def content(self, content: AssetContent[Asset[T]]):
        self._content = content

    @property
    def source(self) -> AssetContentSource:
        return self._source

    @property
    def extension(self):
        raise NotImplementedError

    @classmethod
    def from_string(cls, string: str) -> Asset[T]:
        return cls(content=StringAssetContent(string), source=None)

    @classmethod
    def from_source(cls, source: AssetContentSource, **kwargs):
        return cls(content=AssetContentCache(content_or_source=source), source=source, **kwargs)


class AssetGroup(Generic[T], ABC):
    @property
    @abstractmethod
    def assets(self) -> Iterable[Asset[T]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def deep_assets(self) -> Iterable[Asset[T]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def subgroups(self) -> Iterable[AssetGroup[T]]:
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
    def __init__(self, default_content_type: Optional[Type[AssetContent]] = None):
        self._default_content_type = default_content_type

    @abstractmethod
    def load(self) -> AssetContent:
        raise NotImplementedError


class RuntimeContentSource(AssetContentSource):
    def __init__(self, content: AssetContent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._content = content

    def load(self) -> AssetContent:
        if self._default_content_type is not None and not isinstance(self._content, self._default_content_type):
            return self._default_content_type.from_string(self._content.load().to_string())

        return self._content.to_string()


class FileContentSource(AssetContentSource):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> AssetContent:
        with open(self._path) as f:
            string_content = f.read()

        if self._default_content_type is not None:
            return self._default_content_type.from_string(string_content)

        return StringAssetContent(string_content)


class AssetContentCache:
    def __init__(
            self,
            content_or_source: Union[AssetContentSource, AssetContent],
            default_content_type: Optional[Type[AssetContent]] = None
    ):
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


AssetContent.register(AssetContentCache)