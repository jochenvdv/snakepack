from snakepack.assets import Asset
from snakepack.bundlers import Bundle
from snakepack.bundlers._base import Bundler


class BundleTest:
    def test_init(self, mocker):
        bundler = mocker.MagicMock(spec=Bundler)
        asset1 = mocker.MagicMock(spec=Asset)
        asset2 = mocker.MagicMock(spec=Asset)
        assets = [asset1, asset2]
        bundle = Bundle(name='bundle1', bundler=bundler, assets=assets)

        assert bundle.name == 'bundle1'
        assert bundle.bundler is bundler
        assert bundle.assets == assets

    def test_bundle(self, mocker):
        bundler = mocker.MagicMock(spec=Bundler)
        assets = []

        bundle = Bundle(name='bundle1', bundler=bundler, assets=assets)
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

