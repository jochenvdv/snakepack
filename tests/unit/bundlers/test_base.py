from snakepack.assets import Asset
from snakepack.bundlers import Bundle
from snakepack.bundlers._base import Bundler
from snakepack.loaders import Loader
from snakepack.transformers import Transformer


class BundleTest:
    def test_init(self, mocker):
        bundler = mocker.MagicMock(spec=Bundler)
        loader = mocker.MagicMock(spec=Loader)
        transformers = [
            mocker.MagicMock(spec=Transformer),
            mocker.MagicMock(spec=Transformer)
        ]

        bundle = Bundle(name='bundle1', bundler=bundler, loader=loader, transformers=transformers)

        assert bundle.name == 'bundle1'
        assert bundle.bundler is bundler
        assert bundle.loader == loader
        assert bundle.transformers == transformers

    def test_bundle(self, mocker):
        bundler = mocker.MagicMock(spec=Bundler)
        loader = mocker.MagicMock(spec=Bundler)
        assets = []
        transformers = []

        bundle = Bundle(name='bundle1', bundler=bundler, loader=loader, transformers=transformers)
        bundle.bundle()

        bundler.bundle.assert_called_once_with(bundle)


class BundlerTest:
    class TestBundler(Bundler):
        def bundle(self, bundle: Bundle):
            pass

    def test_init(self, mocker):
        bundle = mocker.MagicMock(spec=Bundle)
        bundler = self.TestBundler()

        bundler.bundle(bundle)

