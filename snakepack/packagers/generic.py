from __future__ import annotations

from pathlib import Path

from snakepack.config import Options
from snakepack.packagers import Packager, Package


class DirectoryPackager(Packager):
    def package(self, package: Package):
        output_path = Path(self._options.output_path.format(package_name=package.name))
        output_path.mkdir(parents=True, exist_ok=True)

        for bundle in package.bundles.values():
            bundle.bundle()

    class Options(Options):
        output_path: str = '{package_name}'

    __config_name__ = 'directory'