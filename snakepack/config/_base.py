from __future__ import annotations

from pydantic import BaseModel


class _ConfigModel(BaseModel):
    class Config:
        copy_on_model_validation = False


class ConfigException(Exception):
    pass


def register_components():
    from snakepack.bundlers import __all__
    from snakepack.packagers import __all__
    from snakepack.loaders import __all__
    from snakepack.transformers import __all__