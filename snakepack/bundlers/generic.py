from pathlib import Path

from snakepack.bundlers import Bundler, Bundle
from snakepack.config import Options


class FileBundler(Bundler):
    def bundle(self, bundle: Bundle):
        for asset in bundle.assets:
            output_path = self._options.output_path.format(bundle_name=asset.name)

            with open(output_path, 'w+') as f:
                f.write(str(asset.content))

    class Options(Options):
        output_path: str = '{bundle_name}'

    __config_name__ = 'file'