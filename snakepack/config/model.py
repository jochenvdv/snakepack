from __future__ import annotations

from pathlib import Path
from typing import Mapping, Union, TypeVar, Generic, Iterable, Sequence

from pydantic import BaseModel

from snakepack.bundlers import Bundler, Bundle
from snakepack.config.options import ComponentConfig
from snakepack.config.types import PythonVersion
from snakepack.loaders import Loader
from snakepack.packagers import Packager, Package
from snakepack.transformers import Transformer


class GlobalOptions(BaseModel):
    source_base_path: Path = Path('./')
    target_base_path: Path = Path('dist/')
    target_version: PythonVersion = PythonVersion.current()
    ignore_errors: bool = True


class BundleConfig(BaseModel):
    bundler: ComponentConfig[Bundler]
    loader: ComponentConfig[Loader]
    transformers: Sequence[ComponentConfig[Transformer]]


class PackageConfig(BaseModel):
    packager: ComponentConfig[Packager]
    bundles: Mapping[str, BundleConfig] = {}


class SnakepackConfig(GlobalOptions):
    packages: Mapping[str, PackageConfig] = {}
