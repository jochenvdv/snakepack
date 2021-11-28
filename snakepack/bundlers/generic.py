from pathlib import Path

from snakepack.bundlers import Bundler, Bundle
from snakepack.config.options import Options
from snakepack.packagers import Package


class FileBundler(Bundler):
    def bundle(self, bundle: Bundle, package: Package):
        for asset in bundle.asset_group.deep_assets:
            bundle_name = asset.full_name.replace('.', '/')
            output_path = package.target_path / Path(self._options.output_path.format(bundle_name=bundle_name))
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w+') as f:
                f.write(str(asset.content))

    class Options(Options):
        output_path: str = '{bundle_name}.py'

    __config_name__ = 'file'


__all__ = [
    FileBundler
]