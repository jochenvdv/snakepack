from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel
from pydantic.generics import GenericModel


class Options(BaseModel, ABC):
    pass


class ConfigurableComponent(ABC):
    __config_name__ = NotImplemented

    def __init__(self, options: Optional[Options] = None):
        if options is None:
            self._options = self.Options()
        else:
            self._options = options

    @property
    def options(self):
        return self._options

    class Options(Options):
        pass


T = TypeVar('T')


class ComponentConfig(GenericModel, Generic[T]):
    name: str
    options: Optional[Options] = None


