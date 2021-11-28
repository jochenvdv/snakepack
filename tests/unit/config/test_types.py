import platform
import sys

import pytest

from snakepack.config.types import PythonVersion, FullyQualifiedPythonName


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


class FullyQualifiedPythonNameTest:
    def test_full_nested(self):
        fqn = FullyQualifiedPythonName('pkg.module:class.attr')

        assert fqn.module_path == ['pkg', 'module']
        assert fqn.ident_path == ['class', 'attr']
        assert fqn.has_module_path
        assert fqn.has_ident_path

    def test_uppercase(self):
        fqn = FullyQualifiedPythonName('Somekg.config.model:SnakepackConfig')

    def test_full_nested_deep(self):
        fqn = FullyQualifiedPythonName('bigpkg.pkg.module:class.attr.anattr')

        assert fqn.module_path == ['bigpkg', 'pkg', 'module']
        assert fqn.ident_path == ['class', 'attr', 'anattr']
        assert fqn.has_module_path
        assert fqn.has_ident_path

    def test_validate_full_shallow(self):
        fqn = FullyQualifiedPythonName('module:class')

        assert fqn.module_path == ['module']
        assert fqn.ident_path == ['class']
        assert fqn.has_module_path
        assert fqn.has_ident_path

    def test_validate_single_nested(self):
        fqn = FullyQualifiedPythonName('pkg.module')

        assert fqn.module_path == ['pkg', 'module']
        assert fqn.ident_path == []
        assert fqn.has_module_path
        assert not fqn.has_ident_path

    def test_validate_single_shallow(self):
        fqn = FullyQualifiedPythonName('module')

        assert fqn.module_path == ['module']
        assert fqn.ident_path == []
        assert fqn.has_module_path
        assert not fqn.has_ident_path

    def test_validate_single_wrong_nesting_punctuation(self):
        with pytest.raises(ValueError):
            fqn = FullyQualifiedPythonName('.module')

    def test_validate_full_wrong_nesting_punctuation(self):
        with pytest.raises(ValueError):
            fqn = FullyQualifiedPythonName('module:.attr')

    def test_validate_blocking_separator(self):
        with pytest.raises(ValueError):
            fqn = FullyQualifiedPythonName(':attr')

    def test_validate_hanging_separator(self):
        with pytest.raises(ValueError):
            fqn = FullyQualifiedPythonName('module:')

    def test_validate_empty(self):
        with pytest.raises(ValueError):
            fqn = FullyQualifiedPythonName('')

    def test_validate_separator_only(self):
        with pytest.raises(ValueError):
            fqn = FullyQualifiedPythonName(':')
