from __future__ import annotations

from typing import Iterable

from boltons.iterutils import first, flatten
from libcst import Module, parse_module

from snakepack.assets import (
    Asset,
    AssetContent,
    AssetGroup,
    AssetType
)


Python = AssetType.create('Python')


class PythonModule(Asset[Python]):
    def __init__(self, full_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._full_name = full_name
        self._name = full_name.split('.')[-1]

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def name(self) -> str:
        return self._name


class PythonModuleCst(AssetContent[PythonModule]):
    def __init__(self, cst: Module):
        self._cst = cst

    def __str__(self):
        return self._cst.code

    @property
    def cst(self) -> Module:
        return self._cst

    @classmethod
    def from_string(cls, string_content) -> AssetContent:
        return PythonModuleCst(cst=parse_module(string_content))


class PythonPackage(AssetGroup[Python]):
    def __init__(self, full_name: str, modules: Iterable[PythonModule], subpackages: Iterable[PythonPackage]):
        self._full_name = full_name
        self._name = full_name.split('.')[-1]
        self._modules = modules
        self._subpackages = subpackages
        self._init_module = first(module for module in modules if module.name == '__init__')

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def modules(self) -> Iterable[PythonModule]:
        return self._modules

    @property
    def subpackages(self) -> Iterable[PythonPackage]:
        return self._subpackages

    @property
    def init_module(self) -> PythonModule:
        return self._init_module

    @property
    def assets(self) -> Iterable[Asset[Python]]:
        return [
            *self._modules,
            *flatten(
                subpackage.assets for subpackage in self._subpackages
            )
        ]


class PythonApplication(AssetGroup[Python]):
    def __init__(self, entry_point: PythonModule, modules: Iterable[PythonModule]):
        self._entry_point = entry_point
        self._modules = modules

    @property
    def modules(self) -> Iterable[PythonModule]:
        return self._modules

    @property
    def entry_point(self) -> PythonModule:
        return self._entry_point

    @property
    def assets(self) -> Iterable[Asset[Python]]:
        return self._modules
