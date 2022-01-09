from pathlib import Path

from snakepack.assets._base import BinaryAssetContent
from snakepack.bundlers import Bundler, Bundle
from snakepack.config.options import Options
from snakepack.packagers import Package


class FileBundler(Bundler):
    def bundle(self, bundle: Bundle, package: Package):
        for asset in bundle.asset_group.deep_assets:
            output_path = package.target_path / Path(self._options.output_path.format(asset_target_path=str(asset.target_path)))
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(asset.content, BinaryAssetContent):
                with open(output_path, 'wb+') as f:
                    f.write(bytes(asset.content))
            else:
                with open(output_path, 'w+') as f:
                    f.write(str(asset.content))

    class Options(Options):
        output_path: str = '{asset_target_path}'

    __config_name__ = 'file'


__all__ = [
    FileBundler
]