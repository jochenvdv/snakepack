from __future__ import annotations

from pathlib import Path
from typing import Mapping, Union, TypeVar, Generic, Iterable, Sequence

from pydantic import BaseModel

from snakepack.bundlers import Bundler, Bundle
from snakepack.config import ComponentConfig, GlobalOptions
from snakepack.config.types import PythonVersion
from snakepack.loaders import Loader
from snakepack.packagers import Packager, Package
from snakepack.transformers import Transformer


class BundleConfig(BaseModel):
    bundler: ComponentConfig[Bundler]
    loader: ComponentConfig[Loader]
    transformers: Sequence[ComponentConfig[Transformer]]


class PackageConfig(BaseModel):
    packager: ComponentConfig[Packager]
    bundles: Mapping[str, BundleConfig] = {}


class SnakepackConfig(GlobalOptions):
    packages: Mapping[str, PackageConfig] = {}
