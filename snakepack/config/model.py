from __future__ import annotations

from pathlib import Path
from typing import Mapping, Union, TypeVar, Generic, Iterable

from pydantic import BaseModel

from snakepack.bundlers import Bundler
from snakepack.config import ComponentConfig
from snakepack.loaders import Loader
from snakepack.packagers import Packager


class BundleConfig(BaseModel):
    bundler: ComponentConfig[Bundler]
    loader: ComponentConfig[Loader]


class PackageConfig(BaseModel):
    packager: ComponentConfig[Packager]
    bundles: Mapping[str, BundleConfig] = {}


class SnakepackConfig(BaseModel):
    source_base_path: Path = Path('./')
    target_base_path: Path = Path('dist/')

    packages: Mapping[str, PackageConfig] = {}