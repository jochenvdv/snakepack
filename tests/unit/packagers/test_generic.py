import os.path

from snakepack.bundlers import Bundler, Bundle
from snakepack.packagers import Package
from snakepack.packagers.generic import DirectoryPackager


class DirectoryPackagerTest:
    def test_config_name(self):
        assert DirectoryPackager.__config_name__ == 'directory'

    def test_init(self):
        options = DirectoryPackager.Options(output_path='test')
        packager = DirectoryPackager(options)

    def test_init_default_options(self):
        packager = DirectoryPackager()

        assert packager.options.output_path == '{package_name}'

    def test_package(self, mocker, fs):
        options = DirectoryPackager.Options(output_path='{package_name}')
        packager = DirectoryPackager(options)

        bundle1 = mocker.MagicMock(spec=Bundle)
        bundle2 = mocker.MagicMock(spec=Bundle)
        bundles = {
            'bundle1': bundle1,
            'bundle2': bundle2
        }

        package = mocker.MagicMock(spec=Package)
        package.name = 'mypackage'
        package.bundles = bundles

        packager.package(package)

        assert os.path.isdir('mypackage')
        bundle1.bundle.assert_called_once()
        bundle2.bundle.assert_called_once()
