from pathlib import Path

from snakepack.bundlers import Bundler, Bundle


class FileBundler(Bundler):
    def __init__(self, output_path: str):
        self._output_path = output_path

    def bundle(self, bundle: Bundle):
        for asset in bundle.assets:
            output_path = self._output_path.format(bundle_name=asset.name)

            with open(output_path, 'w+') as f:
                f.write(str(asset.content))
