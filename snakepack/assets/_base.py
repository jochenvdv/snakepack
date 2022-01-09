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
    def __init__(self, name: str, target_path: Path, content: AssetContent[Asset[T]], source: AssetContentSource):
        self._name = name
        self._target_path = target_path
        self._content = content
        self._source = source

    @property
    def name(self) -> str:
        return self._name

    @property
    def target_path(self) -> Path:
        return self._target_path

    @property
    def content(self) -> AssetContent[Asset[T]]:
        return self._content

    @content.setter
    def content(self, content: AssetContent[Asset[T]]):
        self._content = content

    @property
    def source(self) -> AssetContentSource:
        return self._source

    @classmethod
    def from_string(cls, name: str, target_path: Path, content: str) -> Asset[T]:
        return cls(name=name, target_path=target_path, content=StringAssetContent(content), source=None)

    @classmethod
    def from_source(cls, name: str, target_path: Path, source: AssetContentSource, **kwargs):
        return cls(name=name, target_path=target_path, content=AssetContentCache(content_or_source=source), source=source, **kwargs)


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


class GenericAssetGroup(AssetGroup[T]):
    def __init__(self, assets: Iterable[Asset[T]]):
        self._assets = assets

    @property
    def assets(self) -> Iterable[Asset[T]]:
        return self._assets

    @property
    def deep_assets(self) -> Iterable[Asset[T]]:
        return self._assets

    @property
    def subgroups(self) -> Iterable[AssetGroup[T]]:
        return []


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

    def __bytes__(self) -> bytes:
        return self._string.encode('utf-8')

    @classmethod
    def from_string(cls, string_content) -> StringAssetContent:
        return string_content


class BinaryAssetContent(AssetContent[U]):
    def __init__(self, binary: bytes):
        self._binary = binary

    def __str__(self) -> str:
        return self._binary.decode('utf-8', errors='ignore')

    def __bytes__(self) -> bytes:
        return self._binary

    @classmethod
    def from_string(cls, string_content) -> BinaryAssetContent:
        return cls(bytes(string_content))


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
    def __init__(self, path, binary=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = path
        self._binary = binary

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> AssetContent:
        if self._binary:
            with open(self._path, 'rb') as f:
                binary_content = f.read()
                content = BinaryAssetContent(binary_content)
        else:
            with open(self._path, 'r') as f:
                string_content = f.read()

                if self._default_content_type is not None:
                    content = self._default_content_type.from_string(string_content)
                else:
                    content = StringAssetContent(string_content)

        return content


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

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)

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