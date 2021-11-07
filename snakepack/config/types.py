from __future__ import annotations

import re
import sys
from enum import Enum, unique
from typing import Sequence, Optional, Match, Union


@unique
class PythonVersion(Enum):
    PYTHON_37 = '3.7'
    PYTHON_38 = '3.8'
    PYTHON_39 = '3.9'

    @classmethod
    def current(cls) -> PythonVersion:
        return PythonVersion(f'{sys.version_info[0]}.{sys.version_info[1]}')


class FullyQualifiedPythonName(str):
    _MODULE_NAME_REGEX = r'([a-z0-9_]+)(\.[a-z0-9_]+)*'
    _IDENTIFIER_NAME_REGEX = r'([a-z_][a-z0-9_]*)(\.[a-z_][a-z0-9_]*)*'

    _REGEX = re.compile(
        rf'^(?P<module_path>{_MODULE_NAME_REGEX})(:(?P<ident_path>{_IDENTIFIER_NAME_REGEX}))?$'
    )

    def __new__(cls, value: Union[str, Match]):
        match = cls._REGEX.fullmatch(value)

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
