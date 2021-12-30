from snakepack.assets import AssetType, Asset


GenericAsset = AssetType.create('StaticFile')


class StaticFile(Asset[GenericAsset]):
    pass
