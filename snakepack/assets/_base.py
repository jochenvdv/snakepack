from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TypeVar, Protocol, Optional, Union, Generic


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


class AssetContent(Generic[U]):
    def to_string(self) -> StringAssetContent:
        return StringAssetContent(str(self))

    @abstractmethod
    def __str__(self):
        raise NotImplementedError


class StringAssetContent(AssetContent[U]):
    def __init__(self, string: str):
        self._string = string

    @abstractmethod
    def __str__(self) -> str:
        return self._string





