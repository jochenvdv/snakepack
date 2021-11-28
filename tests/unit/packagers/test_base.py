from pathlib import Path

from snakepack.bundlers import Bundle
from snakepack.config.model import GlobalOptions
from snakepack.packagers import Packager, Package


class PackageTest:
    def test_init(self, mocker):
        packager = mocker.MagicMock(spec=Packager)
        bundle1 = mocker.MagicMock(spec=Bundle)
        bundle1.name = 'bundle1'
        bundle2 = mocker.MagicMock(spec=Bundle)
        bundle2.name = 'bundle2'
        bundles = [bundle1, bundle2]

        package = Package(name='main', packager=packager, bundles=bundles)

        assert package.name == 'main'
        assert package.packager is packager
        assert package.bundles == {
            'bundle1': bundle1,
            'bundle2': bundle2
        }

    def test_package(self, mocker):
        packager = mocker.MagicMock(spec=Packager)
        bundles = []

        package = Package(name='main', packager=packager, bundles=bundles)
        package.package()

        packager.package.assert_called_once_with(package)


class PackagerTest:
    class TestPackager(Packager):
        def package(self, package: Package):
            pass

        def get_target_path(self, package: Package) -> Path:
            return Path(package.name)

    def test_init(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        packager = self.TestPackager(global_options=global_options)

    def test_package(self, mocker):
        global_options = mocker.MagicMock(spec=GlobalOptions)
        packager = self.TestPackager(global_options=global_options)
        package = mocker.MagicMock(spec=Package)

        packager.package(package)
