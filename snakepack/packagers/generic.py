from __future__ import annotations

from pathlib import Path

from snakepack.config.options import Options
from snakepack.packagers import Packager, Package


class DirectoryPackager(Packager):
    def get_target_path(self, package: Package) -> Path:
        return self._global_options.target_base_path / Path(self._options.output_path.format(package_name=package.name))

    def package(self, package: Package):
        output_path = self.get_target_path(package)
        output_path.mkdir(parents=True, exist_ok=True)

        for bundle in package.bundles.values():
            bundle.bundle(package=package)

    class Options(Options):
        output_path: str = '{package_name}'

    __config_name__ = 'directory'


__all__ = [
    DirectoryPackager
]