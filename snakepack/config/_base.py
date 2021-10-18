from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar, Optional, Mapping, Any

from pydantic import BaseModel, root_validator, validator
from pydantic.generics import GenericModel


class _ConfigModel(BaseModel):
    class Config:
        copy_on_model_validation = False


class Options(_ConfigModel, ABC):
    pass


class ConfigurableComponent(ABC):
    __config_name__ = NotImplemented
    __component_types__ = {}

    def __init__(self, options: Optional[Options] = None):
        if options is None:
            self._options = self.Options()
        else:
            self._options = options

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

    @validator('options', allow_reuse=True)
    def validate_options(cls, value, values):
        name = values['name']

        if name not in ConfigurableComponent.__component_types__:
            raise ConfigException(f'Unknown component \'{name}\'')

        if value is None:
            return ConfigurableComponent.__component_types__[name].Options()

        if isinstance(value, ConfigurableComponent.__component_types__[name].Options):
            return value

        return ConfigurableComponent.__component_types__[name].Options(**value)

    class Config(_ConfigModel.Config):
        pass


class ConfigException(Exception):
    pass

