from pathlib import Path

from snakepack.packagers import Packager, Package


class DirectoryPackager(Packager):
    def __init__(self, output_path: str):
        self._output_path = output_path

    def package(self, package: Package):
        output_path = Path(self._output_path.format(package_name=package.name))
        output_path.mkdir(parents=True, exist_ok=True)

        for bundle in package.bundles.values():
            bundle.bundle()
