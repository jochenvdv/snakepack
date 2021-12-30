from pathlib import Path
from typing import Sequence

from snakepack.assets import AssetGroup
from snakepack.assets._base import GenericAssetGroup, FileContentSource
from snakepack.assets.generic import StaticFile
from snakepack.config.options import Options
from snakepack.loaders import Loader


class StaticFileLoader(Loader):
    def load(self) -> GenericAssetGroup:
        assets = []

        for path in self._options.paths:
            asset = StaticFile.from_source(
                name=path,
                target_path=path,
                source=FileContentSource(path=path)
            )
            assets.append(asset)

        return GenericAssetGroup(assets=assets)

    class Options(Options):
        paths: Sequence[Path] = []


__all__ = [
    StaticFileLoader
]