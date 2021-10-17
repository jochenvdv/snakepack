from pathlib import Path

from snakepack.bundlers import Bundler
from snakepack.config import ComponentConfig
from snakepack.config.model import SnakepackConfig, BundleConfig, PackageConfig
from snakepack.loaders import Loader
from snakepack.packagers import Packager
from snakepack.transformers import Transformer


class BundleConfigTest:
    def test_init(self, mocker):
        bundler_config = mocker.MagicMock(spec=ComponentConfig[Bundler])
        loader_config = mocker.MagicMock(spec=ComponentConfig[Loader])
        transformer_configs = [
            mocker.MagicMock(spec=ComponentConfig[Transformer]),
            mocker.MagicMock(spec=ComponentConfig[Transformer])
        ]

        config = BundleConfig(
            bundler=bundler_config,
            loader=loader_config,
            transformers=transformer_configs
        )

        assert config.bundler == bundler_config
        assert config.loader == loader_config
        assert config.transformers == transformer_configs


class PackageConfigTest:
    def test_init(self, mocker):
        bundles = {}
        packager_config = mocker.MagicMock(spec=ComponentConfig[Packager])

        config = PackageConfig(
            packager=packager_config,
            bundles=bundles
        )

        assert config.bundles == bundles
        assert config.packager == packager_config


class SnakepackConfigTest:
    def test_init(self, mocker):
        source_base_path = Path('./')
        target_base_path = Path('dist/')

        package = mocker.MagicMock(spec=PackageConfig)

        config = SnakepackConfig(
            source_base_path=source_base_path,
            target_base_path=target_base_path,
            packages={
                'test': package
            }
        )

        assert config.source_base_path == source_base_path
        assert config.target_base_path == target_base_path

    def test_init_defaults(self):
        config = SnakepackConfig()

        assert config.source_base_path == Path('./')
        assert config.target_base_path == Path('dist/')
        assert config.packages == {}