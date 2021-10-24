from __future__ import annotations

import sys
from enum import Enum, unique


@unique
class PythonVersion(Enum):
    PYTHON_37 = '3.7'
    PYTHON_38 = '3.8'
    PYTHON_39 = '3.9'

    @classmethod
    def current(cls) -> PythonVersion:
        return PythonVersion(f'{sys.version_info[0]}.{sys.version_info[1]}')