import os

from snakepack.assets import Asset, AssetContent
from snakepack.bundlers import Bundle
from snakepack.bundlers.generic import FileBundler


class FileBundlerTest:
    def test_init(self):
        bundler = FileBundler(output_path='test')

    def test_bundle(self, mocker, fs):
        bundler = FileBundler(output_path='{bundle_name}.py')

        asset1 = mocker.MagicMock(spec=Asset)
        content1 = mocker.MagicMock(spec=AssetContent)
        content1.__str__.return_value = 'test=True'
        asset1.content = content1
        asset1.name = 'asset1'

        asset2 = mocker.MagicMock(spec=Asset)
        content2 = mocker.MagicMock(spec=AssetContent)
        content2.__str__.return_value = 'test=False'
        asset2.content = content2
        asset2.name = 'asset2'

        assets = [asset1, asset2]
        bundle = Bundle(name='test', bundler=bundler, assets=assets)

        bundler.bundle(bundle)

        assert os.path.exists('asset1.py')

        with open('asset1.py') as f:
            assert f.read() == 'test=True'

        assert os.path.exists('asset2.py')

        with open('asset2.py') as f:
            assert f.read() == 'test=False'
