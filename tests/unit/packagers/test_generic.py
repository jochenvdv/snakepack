import os.path

from snakepack.bundlers import Bundler, Bundle
from snakepack.config.model import GlobalOptions
from snakepack.packagers import Package
from snakepack.packagers.generic import DirectoryPackager


class DirectoryPackagerTest:
    def test_config_name(self):
        assert DirectoryPackager.__config_name__ == 'directory'

    def test_init(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        options = DirectoryPackager.Options(output_path='test')
        packager = DirectoryPackager(global_options=global_options, options=options)

    def test_init_default_options(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        packager = DirectoryPackager(global_options=global_options)

        assert packager.options.output_path == '{package_name}'

    def test_package(self, mocker, fs):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        global_options.target_base_path = 'dist/'
        options = DirectoryPackager.Options(output_path='{package_name}')
        packager = DirectoryPackager(global_options=global_options, options=options)

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

        assert os.path.isdir('dist/mypackage')
        bundle1.bundle.assert_called_once()
        bundle2.bundle.assert_called_once()
