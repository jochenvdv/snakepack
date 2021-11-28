from abc import ABC
from pathlib import Path
from typing import Generic, Optional, Any, Type, TypeVar, List

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel

from snakepack.config._base import _ConfigModel
from snakepack.config.types import Selector


class Options(_ConfigModel, ABC):
    includes: List[Selector] = []
    excludes: List[Selector] = []


class ConfigurableComponent(ABC):
    __config_name__ = NotImplemented
    __component_types__ = {}

    def __init__(self, global_options: Options, options: Optional[Options] = None):
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

    def initialize_component(self, global_options: Options):
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


class Selectable(ABC):
    def matches(self, selector: Selector) -> bool:
        raise NotImplementedError


class SelectiveComponent(ConfigurableComponent):
    @property
    def includes(self) -> List[Selector]:
        return self._options.includes

    @property
    def excludes(self) -> List[Selector]:
        return self._options.excludes

    def selects(self, target):
        return any(map(lambda x: x.matches(target), self._options.excludes))

