from __future__ import annotations

import re
import sys
from abc import ABC
from enum import Enum, unique
from typing import Sequence, Optional, Match, Union


class Selector(ABC, str):
    REGEX = NotImplemented
    _selector_types = set()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        Selector._selector_types.add(cls)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        for selector_type in cls._selector_types:
            if selector_type.REGEX.fullmatch(value):
                return selector_type(value)

        raise ValueError(f"Invalid selector '{value}'")

@unique
class PythonVersion(Enum):
    PYTHON_37 = '3.7'
    PYTHON_38 = '3.8'
    PYTHON_39 = '3.9'
    PYTHON_310 = '3.10'

    @classmethod
    def current(cls) -> PythonVersion:
        return PythonVersion(f'{sys.version_info[0]}.{sys.version_info[1]}')


class FullyQualifiedPythonName(Selector):
    _MODULE_NAME_REGEX = r'([a-zA-Z0-9_]+)(\.[a-zA-Z0-9_]+)*'
    _IDENTIFIER_NAME_REGEX = r'([a-zA-Z_][a-zA-Z0-9_]*)(\.[a-zA-Z_][a-zA-Z0-9_]*)*'

    REGEX = re.compile(
        rf'^(?P<module_path>{_MODULE_NAME_REGEX})(:(?P<ident_path>{_IDENTIFIER_NAME_REGEX}))?$'
    )

    def __new__(cls, value: Union[str, Match]):
        match = cls.REGEX.fullmatch(value)

        if not match:
            raise ValueError('Invalid fully qualified python name')

        module_path = match.group('module_path')
        ident_path = match.group('ident_path')

        mod_path_elems = []

        if module_path is not None:
            mod_path_elems.extend(module_path.split('.'))

        id_path_elems = []

        if ident_path is not None:
            id_path_elems.extend(ident_path.split('.'))

        obj = str.__new__(cls, value)

        obj._module_path = mod_path_elems
        obj._ident_path = id_path_elems

        return obj

    @property
    def module_path(self) -> Sequence[str]:
        return list(self._module_path)

    @property
    def ident_path(self) -> Sequence[str]:
        return list(self._ident_path)

    @property
    def has_module_path(self) -> bool:
        return len(self._module_path) > 0

    @property
    def has_ident_path(self) -> bool:
        return len(self._ident_path) > 0

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        return cls(value)
