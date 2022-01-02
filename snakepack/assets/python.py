from __future__ import annotations

from pathlib import Path
from typing import Iterable

from boltons.iterutils import first, flatten
from libcst import Module, parse_module, MetadataWrapper

from snakepack.assets import (
    Asset,
    AssetContent,
    AssetGroup,
    AssetType
)
from snakepack.assets._base import T, StringAssetContent, AssetContentSource, AssetContentCache
from snakepack.assets.generic import StaticFile
from snakepack.config.options import Selectable, Selector
from snakepack.config.types import FullyQualifiedPythonName

Python = AssetType.create('Python')


class PythonModule(Asset[Python]):
    def __init__(self, name: str, *args, **kwargs):
        target_path = Path(f"{name.replace('.', '/')}.py")
        super().__init__(name, target_path, *args, **kwargs)

    @property
    def name(self) -> str:
        return self._name

    def matches(self, selector: Selector) -> bool:
        if not isinstance(selector, FullyQualifiedPythonName):
            return False

        return not selector.has_module_path or selector.has_ident_path or self._name.startswith('.'.join(selector.module_path))

    @classmethod
    def from_string(cls, name: str, content: str, **kwargs) -> Asset[T]:
        return cls(name=name, content=StringAssetContent(content), source=None)

    @classmethod
    def from_source(cls, name: str,source: AssetContentSource, **kwargs):
        return cls(
            name=name,
            content=AssetContentCache(content_or_source=source),
            source=source,
            **kwargs
        )


class PythonModuleCst(AssetContent[PythonModule]):
    def __init__(self, cst: Module):
        self._wrapper = MetadataWrapper(module=cst)

    def __str__(self):
        return self._wrapper.module.code

    @property
    def cst(self) -> Module:
        return self._wrapper.module

    @property
    def metadata_wrapper(self):
        return self._wrapper

    @classmethod
    def from_string(cls, string_content) -> AssetContent:
        return PythonModuleCst(cst=parse_module(str(string_content)))


class PythonPackage(AssetGroup[Python]):
    def __init__(
            self,
            full_name: str,
            modules: Iterable[PythonModule],
            subpackages: Iterable[PythonPackage],
            data_files: Iterable[StaticFile]
    ):
        self._full_name = full_name
        self._name = full_name.split('.')[-1]
        self._modules = modules
        self._subpackages = subpackages
        self._data_files = data_files
        self._init_module = first(module for module in modules if module.name.split('.')[-1] == '__init__')

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def init_module(self) -> PythonModule:
        return self._init_module

    @property
    def assets(self) -> Iterable[Asset[Python]]:
        return self._modules

    @property
    def deep_assets(self) -> Iterable[Asset[T]]:
        return [
            *self._modules,
            *flatten(
                subpackage.deep_assets for subpackage in self._subpackages
            ),
            *self._data_files
        ]

    @property
    def subgroups(self) -> Iterable[AssetGroup[T]]:
        return self._subpackages


class PythonApplication(AssetGroup[Python]):
    def __init__(self, entry_point: PythonModule, packages: Iterable[PythonPackage], modules: Iterable[PythonModule]):
        self._entry_point = entry_point
        self._packages = packages
        self._modules = modules

    @property
    def entry_point(self) -> PythonModule:
        return self._entry_point

    @property
    def assets(self) -> Iterable[Asset[Python]]:
        return self._modules

    @property
    def deep_assets(self) -> Iterable[Asset[T]]:
        return [
            *self._modules,
            *flatten(
                package.deep_assets for package in self._packages
            )
        ]

    @property
    def subgroups(self) -> Iterable[AssetGroup[T]]:
        return self._packages