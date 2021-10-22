from collections import namedtuple
from typing import Optional, Dict, Iterable, List

from snakepack.assets import AssetContentSource, Asset
from snakepack.bundlers import Bundle
from snakepack.config import ComponentConfig
from snakepack.config.model import SnakepackConfig, PackageConfig, BundleConfig
from snakepack.loaders import Loader
from snakepack.packagers import Package
from snakepack.transformers import Transformer


class Compiler:
    def __init__(self, config: SnakepackConfig):
        self._config = config
        self._packages: List[Package] = []

    def run(self):
        self._load_packages()
        self._load_assets()
        self._transform_assets()

    def _load_packages(self):
        for package_name, package_config in self._config.packages:
            packager = package_config.packager.initialize_component()
            bundles = []

            for bundle_name, bundle_config in package_config.bundles:
                bundler = bundle_config.bundler.initialize_component()
                loader = bundle_config.loader.initialize_component()
                transformers = [transformer.initialize_component() for transformer in bundle_config.transformers]

                bundle = Bundle(name=bundle_name, bundler=bundler, loader=loader, transformers=transformers)
                bundles.append(bundle)

            package = Package(name=package_name, packager=packager, bundles=bundles)
            self._packages.append(package)

    def _load_assets(self):
        for package in self._packages:
            for bundle in package.bundles.values():
                bundle.load()

    def _transform_assets(self):
        for package in self._packages:
            for bundle in package.bundles.values():
                for asset in bundle.assets:
                    for transformer in bundle.transformers:
                        transformer.transform(asset)