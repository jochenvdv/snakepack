from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import Generic, TypeVar, Optional, Mapping, Any, Type, Iterable

from pydantic import BaseModel, root_validator, validator
from pydantic.generics import GenericModel

from snakepack.config.types import PythonVersion


class _ConfigModel(BaseModel):
    class Config:
        copy_on_model_validation = False


class Options(_ConfigModel, ABC):
    pass


class GlobalOptions(BaseModel):
    source_base_path: Path = Path('./')
    target_base_path: Path = Path('dist/')
    target_version: PythonVersion = PythonVersion.current()


class ConfigurableComponent(ABC):
    __config_name__ = NotImplemented
    __component_types__ = {}

    def __init__(self, global_options: GlobalOptions, options: Optional[Options] = None):
        self._global_options = global_options

        if options is None:
            self._options = self.Options()
        else:
            self._options = options

    @property
    def global_options(self):
        return self._global_options

    @property
    def options(self):
        return self._options

    @classmethod
    def __init_subclass__(cls, **kwargs):
        ConfigurableComponent.__component_types__[cls.__config_name__] = cls

    class Options(Options):
        pass


T = TypeVar('T')


class ComponentConfig(GenericModel, Generic[T]):
    name: str
    options: Optional[Any] = None
    _component_class: Type[ConfigurableComponent]

    def initialize_component(self, global_options: GlobalOptions):
        return self._get_component_class(self.name)(
            global_options=global_options,
            options=self.options
        )

    @validator('name', pre=True, allow_reuse=True)
    def validate_name(cls, value):
        component_class = cls._get_component_class(value)
        assert component_class is not None, f'Unknown component \'{value}\''
        cls._component_class = component_class
        return value

    @validator('options', always=True, allow_reuse=True)
    def validate_options(cls, value, values):
        if 'name' not in values:
            return

        name = values['name']

        if value is None:
            return ConfigurableComponent.__component_types__[name].Options()

        if isinstance(value, ConfigurableComponent.__component_types__[name].Options):
            return value

        return ConfigurableComponent.__component_types__[name].Options(**value)

    @classmethod
    def _get_component_class(cls, name):
        return ConfigurableComponent.__component_types__.get(name, None)

    class Config(_ConfigModel.Config):
        pass


class ConfigException(Exception):
    pass


def register_components():
    from snakepack.bundlers import __all__
    from snakepack.packagers import __all__
    from snakepack.loaders import __all__
    from snakepack.transformers import __all__