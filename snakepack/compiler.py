from __future__ import annotations

from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Optional, Dict, Iterable, List, Callable, TypeVar, Type

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.assets import AssetContentSource, Asset
from snakepack.assets.python import PythonModuleCst
from snakepack.bundlers import Bundle
from snakepack.config.options import ComponentConfig
from snakepack.config.model import SnakepackConfig, PackageConfig, BundleConfig
from snakepack.loaders import Loader
from snakepack.packagers import Package
from snakepack.transformers import Transformer


class Compiler:
    def __init__(self, config: SnakepackConfig, executor: Executor):
        self._config = config
        self._packages: List[Package] = []
        self._loaders: Dict[Bundle, Loader] = {}
        self._executor = executor

    def run(self):
        self._load_packages()
        self._load_assets()
        self._transform_assets()
        self._package_assets()

    def _load_packages(self):
        for package_name, package_config in self._config.packages.items():
            packager = package_config.packager.initialize_component(global_options=self._config)
            bundles = []

            for bundle_name, bundle_config in package_config.bundles.items():
                bundler = bundle_config.bundler.initialize_component(global_options=self._config)
                loader = bundle_config.loader.initialize_component(global_options=self._config)
                transformers = [
                    transformer.initialize_component(global_options=self._config)
                    for transformer in bundle_config.transformers
                ]

                bundle = Bundle(name=bundle_name, bundler=bundler, loader=loader, transformers=transformers)
                bundles.append(bundle)
                self._loaders[bundle] = loader

            package = Package(name=package_name, packager=packager, bundles=bundles)
            self._packages.append(package)

    def _load_assets(self):
        for package in self._packages:
            for bundle in package.bundles.values():
                bundle.load()

    def _transform_assets(self):
        # this comment should not be removed
        for package in self._packages:
            for bundle in package.bundles.values():
                for asset in bundle.asset_group.deep_assets:
                    for transformer in bundle.transformers:
                        if not any(map(lambda x: asset.matches(x), transformer.options.excludes)):
                            analyses = {
                                analyzer: self._executor.execute(
                                    task_name=f"Running '{analyzer.__config_name__}' analyzer on asset '{asset.full_name}'",
                                    task=lambda: self._run_analysis(bundle, analyzer, asset)
                                )
                                for analyzer in transformer.REQUIRED_ANALYZERS
                            }
                            self._executor.execute(
                                task_name=f"Applying '{transformer.__config_name__}' transformer to asset '{asset.full_name}'",
                                task=lambda: transformer.transform(analyses=analyses, subject=asset)
                            )

    def _package_assets(self):
        for package in self._packages:
            package.package()

    def _run_analysis(self, bundle: Bundle, analyzer_class: Type[Analyzer], subject: Asset) -> Analyzer.Analysis:
        if analyzer_class is not ImportGraphAnalyzer:
            return analyzer_class().analyse(subject)

        return self._loaders[bundle].analysis


T = TypeVar('T')


class Executor(ABC):
    @abstractmethod
    def execute(self, task_name: str, task: Callable[..., T]):
        raise NotImplemented


class SynchronousExecutor(Executor):
    def execute(self, task_name: str, task: Callable[..., T]):
        return task()
