from __future__ import annotations

import os
import traceback
from abc import ABC, abstractmethod
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from logging import Logger
from typing import Optional, Dict, Iterable, List, Callable, TypeVar, Type

from loky import get_reusable_executor

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python import PythonModuleCstAnalyzer
from snakepack.analyzers.python._base import BatchPythonModuleCstAnalyzer
from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.assets import AssetContentSource, Asset
from snakepack.assets.python import PythonModuleCst, PythonModule
from snakepack.bundlers import Bundle
from snakepack.config.options import ComponentConfig
from snakepack.config.model import SnakepackConfig, PackageConfig, BundleConfig
from snakepack.loaders import Loader
from snakepack.packagers import Package
from snakepack.transformers import Transformer
from snakepack.transformers.python._base import BatchablePythonModuleTransformer, BatchPythonModuleTransformer


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
        self._executor.logger.debug("# Initialising components ---")

        for package_name, package_config in self._config.packages.items():
            self._executor.logger.debug(f"... Registering package '{package_name}'")

            packager = package_config.packager.initialize_component(global_options=self._config)
            bundles = []

            for bundle_name, bundle_config in package_config.bundles.items():
                self._executor.logger.debug(f"... Registering bundle '{bundle_name}'")
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
        nested_tasks = []
        task = Task(
            start_msg="# Loading assets into the compiler ---",
            complete_msg='',
            fail_msg="! Failed to load assets into the compiler - exiting",
            nested_tasks=nested_tasks
        )

        for package in self._packages:
            for bundle in package.bundles.values():
                bundle_task = Task(
                    start_msg=f"... Loading assets for bundle '{bundle.name}'",
                    complete_msg='',
                    fail_msg=f"! Failed to load assets for bundle '{bundle.name}' - exiting",
                    callable=bundle.load
                )
                nested_tasks.append(bundle_task)

        list(self._executor.execute(tasks=[task], parallel=False))

    def _transform_assets(self):
        for package in self._packages:
            for bundle in package.bundles.values():
                self._executor.logger.info(f"# Running transformers for package '{package.name}' & bundle '{bundle.name}' ---")
                sync_tasks = []
                parallel_tasks = []

                for asset in bundle.asset_group.deep_assets:
                    if not isinstance(asset, PythonModule):
                        continue

                    transformers = [
                        transformer
                        for transformer in bundle.transformers
                        if not any(map(lambda x: asset.matches(x), transformer.options.excludes))
                    ]

                    batchable_transformers = [t for t in transformers if
                                              isinstance(t, BatchablePythonModuleTransformer)]
                    nonbatchable_transformers = [t for t in transformers if
                                                 not isinstance(t, BatchablePythonModuleTransformer)]
                    batch_transformer = BatchPythonModuleTransformer(
                        batchable_transformers,
                        global_options=self._config
                    )

                    parallel_tasks.append(
                        Task(
                            start_msg=f"... Running simple transformers on asset '{asset.name}'",
                            complete_msg='',
                            fail_msg=f"! Failed to execute simple transformers on asset '{asset.name}'{'- exiting' if self._config.ignore_errors else ''}",
                            callable=partial(
                                Compiler._transform_asset_parallel,
                                asset=asset,
                                transformers=[batch_transformer]
                            )
                        )
                    )

                    sync_tasks.append(
                        Task(
                            start_msg=f"... Running complex transformers on asset '{asset.name}'",
                            complete_msg='',
                            fail_msg=f"! Failed to execute complex transformers on asset '{asset.name}'{'- exiting' if self._config.ignore_errors else ''}",
                            callable=partial(
                                Compiler._transform_asset,
                                asset=asset,
                                transformers=nonbatchable_transformers,
                                import_analysis=self._loaders[bundle].analysis
                            )
                        )
                    )

                list(self._executor.execute(sync_tasks, parallel=False, ignore_errors=self._config.ignore_errors))
                list(self._executor.execute(parallel_tasks, parallel=True, ignore_errors=self._config.ignore_errors))

    def _package_assets(self):
        nested_tasks = []
        task = Task(
            start_msg="# Packaging assets ---",
            complete_msg='',
            fail_msg="! Failed to package assets - exiting",
            nested_tasks=nested_tasks
        )

        for package in self._packages:
            package_task = Task(
                start_msg=f"... Packaging & bundling assets for package '{package.name}'",
                complete_msg='',
                fail_msg=f"! Failed to package & bundle assets for package '{package.name}' - exiting",
                callable=package.package
            )
            nested_tasks.append(package_task)

        list(self._executor.execute(tasks=[task], parallel=False))

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

            try:
                transformer.transform(analyses=analyses, subject=asset)
            except Exception as e:
                traceback.print_exc()
                raise e

    @staticmethod
    def _transform_asset_parallel(asset, transformers):
        for transformer in transformers:
            transformer.transform(analyses={}, subject=asset)


T = TypeVar('T')


class Task:
    def __init__(
            self,
            start_msg: str,
            complete_msg: str,
            fail_msg: str,
            callable: Optional[Callable[..., T]] = None,
            nested_tasks: Optional[List[Task]] = None,
    ):
        self._start_msg = start_msg
        self._complete_msg = complete_msg
        self._fail_msg = fail_msg
        self._callable = callable
        self._result = None

        if nested_tasks is None:
            nested_tasks = []

        self._nested_tasks = nested_tasks

    @property
    def start_msg(self) -> str:
        return self._start_msg

    @property
    def complete_msg(self) -> str:
        return self._complete_msg

    @property
    def fail_msg(self) -> str:
        return self._fail_msg

    @property
    def result(self):
        return self._result

    @property
    def nested_tasks(self) -> List[Task]:
        return self._nested_tasks

    def run(self) -> Task:
        self._result = self._callable()
        return self


class Executor(ABC):
    def __init__(self, logger: Logger):
        self._logger = logger

    @property
    def logger(self) -> Logger:
        return self._logger

    @abstractmethod
    def execute(self, tasks: Iterable[Task], parallel: bool, ignore_errors: bool = False) -> Iterable[Task]:
        raise NotImplemented

    def _execute_task(self, task: Task, ignore_errors: bool):
        self._logger.info(task.start_msg)

        if len(task.nested_tasks) > 0:
            return list(self.execute(task.nested_tasks, parallel=False, ignore_errors=ignore_errors))

        try:
            result = task.run()
            return result
        except Exception as e:
            self._logger.error(task.fail_msg, exc_info=None)

            if not ignore_errors:
                self._logger.critical(task.fail_msg)
                raise e

            return None


class SynchronousExecutor(Executor):
    def execute(self, tasks: Iterable[Task], parallel: bool = False, ignore_errors: bool = False) -> Iterable[Task]:
        return map(
            lambda x: self._execute_task(x, ignore_errors=ignore_errors),
            tasks
        )


class ConcurrentExecutor(Executor):
    def __init__(self, sync_executor: SynchronousExecutor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sync_executor = sync_executor
        os.environ['LOKY_PICKLER'] = 'cloudpickle'
        self._executor = get_reusable_executor()

    def execute(self, tasks: Iterable[Task], parallel: bool = False, ignore_errors: bool = False) -> Iterable[Task]:
        if parallel:
            return self._executor.map(
                lambda x: x.run(),
                tasks
            )

        return self._sync_executor.execute(tasks, ignore_errors=ignore_errors)