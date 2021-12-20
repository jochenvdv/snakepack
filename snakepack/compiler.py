from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Optional, Dict, Iterable, List, Callable, TypeVar, Type

from loky import get_reusable_executor

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.analyzers.python._base import BatchPythonModuleCstAnalyzer
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
        for package in self._packages:
            for bundle in package.bundles.values():
                tasks = []

                for asset in bundle.asset_group.deep_assets:
                    transformers = [
                        transformer
                        for transformer in bundle.transformers
                        if not any(map(lambda x: asset.matches(x), transformer.options.excludes))
                    ]

                    tasks.append(
                        Task(
                            name=f"Transforming '{asset.full_name}'",
                            callable=partial(
                                Compiler._transform_asset,
                                asset=asset,
                                transformers=transformers,
                                import_analysis=self._loaders[bundle].analysis
                            )
                        )
                    )

                for task in self._executor.execute(tasks):
                    print('Ok: ' + task.name)

    def _package_assets(self):
        for package in self._packages:
            package.package()

    @staticmethod
    def _run_analysis(analyzer_class, import_analysis, subject) -> Analyzer.Analysis:
        if analyzer_class is not ImportGraphAnalyzer:
            return analyzer_class().analyse(subject)

        return import_analysis

    @staticmethod
    def _transform_asset(asset, transformers, import_analysis):
        for transformer in transformers:
            batchable_analyzers = []
            analyzers = []
            import_analysis_required = False

            for analyzer in transformer.REQUIRED_ANALYZERS:
                if analyzer is ImportGraphAnalyzer:
                    import_analysis_required = True
                elif issubclass(analyzer, PythonModuleCstAnalyzer):
                    batchable_analyzers.append(analyzer())
                else:
                    analyzers.append(analyzer)

            analyses = {
                analyzer: analyzer().analyse_subject(asset)
                for analyzer in analyzers
            }

            if len(batchable_analyzers) > 0:
                batch_analyzer = BatchPythonModuleCstAnalyzer(batchable_analyzers)
                batch_analyses = batch_analyzer.analyse_subject(asset)
                analyses = {**analyses, **batch_analyses}

            if import_analysis_required:
                analyses[ImportGraphAnalyzer] = import_analysis

            transformer.transform(analyses=analyses, subject=asset)


T = TypeVar('T')


class Task:
    def __init__(self, name: str, callable: Callable[..., T]):
        self._name = name
        self._callable = callable
        self._result = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def result(self):
        return self._result

    def run(self) -> Task:
        self._result = self._callable()
        return self


class Executor(ABC):
    @abstractmethod
    def execute(self, tasks: Iterable[Task]) -> Iterable[Task]:
        raise NotImplemented


class SynchronousExecutor(Executor):
    def execute(self, tasks: Iterable[Task]) -> Iterable[Task]:
        return map(
            lambda x: x.run(),
            tasks
        )


class MultiProcessExecutor(Executor):
    def __init__(self):
        os.environ['LOKY_PICKLER'] = 'cloudpickle'
        self._executor = get_reusable_executor()

    def execute(self, tasks: Iterable[Task]) -> Iterable[Task]:
        return self._executor.map(
            lambda x: x.run(),
            tasks
        )