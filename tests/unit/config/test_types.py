import platform
import sys

from snakepack.config.types import PythonVersion


class PythonVersionTest:
    def test_enum_by_name(self):
        assert PythonVersion.PYTHON_37.value == '3.7'
        assert PythonVersion.PYTHON_38.value == '3.8'
        assert PythonVersion.PYTHON_39.value == '3.9'

    def test_enum_by_value(self):
        assert PythonVersion('3.7') is PythonVersion.PYTHON_37
        assert PythonVersion('3.8') is PythonVersion.PYTHON_38
        assert PythonVersion('3.9') is PythonVersion.PYTHON_39

    def test_current(self):
        version = PythonVersion.current()

        assert isinstance(version, PythonVersion)
        assert version in PythonVersion
        assert platform.python_version().startswith(version.value)