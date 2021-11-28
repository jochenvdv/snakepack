import pytest
from libcst import Module

from snakepack.assets import AssetType, AssetContent
from snakepack.assets.python import Python, PythonModule, PythonModuleCst, PythonPackage, PythonApplication
from snakepack.config.types import FullyQualifiedPythonName


class PythonTest:
    def test_python_asset_type(self):
        assert issubclass(Python, AssetType)


class PythonModuleTest:
    def test_init(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        module = PythonModule(full_name='some.test.module', content=content, source=None)

        assert module.full_name == 'some.test.module'
        assert module.name == 'module'
        assert module.content is content

    def test_matches_returns_true_when_selector_is_full_module_name(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        module = PythonModule(full_name='some.test.module', content=content, source=None)
        selector = mocker.MagicMock(spec=FullyQualifiedPythonName)
        selector.has_module_path = True
        selector.module_path = ['some', 'test', 'module']

        assert module.matches(selector)

    def test_matches_returns_true_when_selector_is_identifier(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        module = PythonModule(full_name='some.test.module', content=content, source=None)
        selector = mocker.MagicMock(spec=FullyQualifiedPythonName)
        selector.has_module_path = False
        selector.has_ident_path = False

        assert module.matches(selector)

    def test_matches_returns_false_when_selector_is_package(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        module = PythonModule(full_name='some.test.module', content=content, source=None)
        selector = mocker.MagicMock(spec=FullyQualifiedPythonName)
        selector.has_module_path = True
        selector.has_ident_path = False
        selector.module_path = ['some', 'test']

        assert not module.matches(selector)

    def test_matches_returns_false_when_selector_is_other_module(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        module = PythonModule(full_name='some.test.module', content=content, source=None)
        selector = mocker.MagicMock(spec=FullyQualifiedPythonName)
        selector.has_module_path = True
        selector.has_ident_path = False
        selector.module_path = ['some', 'test', 'othermodule']

        assert not module.matches(selector)

    def test_matches_returns_false_when_selector_is_identifier(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        module = PythonModule(full_name='some.test.module:some_ident', content=content, source=None)
        selector = mocker.MagicMock(spec=FullyQualifiedPythonName)
        selector.has_module_path = True
        selector.has_ident_path = False
        selector.module_path = ['some', 'test', 'othermodule']

        assert not module.matches(selector)


class PythonModuleCstTest:
    @pytest.mark.skip
    def test_init(self, mocker):
        cst = mocker.MagicMock(spec=Module)
        cst.code = 'x=5'
        content = PythonModuleCst(cst=cst)

        assert content.cst is cst
        assert str(content) == 'x=5'

    @pytest.mark.skip
    def test_from_string(self, mocker):
        parse_module_mock = mocker.patch('libcst.parse_module')
        cst = parse_module_mock.return_value
        content = PythonModuleCst.from_string('x=5')

        assert content.cst is cst


class PythonPackageTest:
    def test_init(self, mocker):
        subpackages = []

        init_module = mocker.MagicMock(spec=PythonModule)
        init_module.full_name = 'mypackage.__init__'
        init_module.name = '__init__'
        module1 = mocker.MagicMock(spec=PythonModule)
        module2 = mocker.MagicMock(spec=PythonModule)
        modules = [init_module, module1, module2]

        package = PythonPackage(full_name='mypackage', modules=modules, subpackages=subpackages)

        assert package.full_name == 'mypackage'
        assert package.name == 'mypackage'
        assert package.subgroups == subpackages
        assert package.assets == modules
        assert package.init_module is init_module
        assert package.deep_assets == modules

    def test_init_with_subpackages(self, mocker):
        sub_init_module = mocker.MagicMock(spec=PythonModule)
        sub_init_module.full_name = 'mypackage.subpackage.__init__'
        sub_init_module.name = '__init__'
        sub_module1 = mocker.MagicMock(spec=PythonModule)
        sub_module2 = mocker.MagicMock(spec=PythonModule)
        sub_modules = [sub_init_module, sub_module1, sub_module2]

        subpackages = [
            PythonPackage(full_name='mypackage.subpackage', modules=sub_modules, subpackages=[])
        ]

        init_module = mocker.MagicMock(spec=PythonModule)
        init_module.full_name = 'mypackage.__init__'
        init_module.name = '__init__'
        module1 = mocker.MagicMock(spec=PythonModule)
        module2 = mocker.MagicMock(spec=PythonModule)
        modules = [init_module, module1, module2]

        package = PythonPackage(full_name='mypackage', modules=modules, subpackages=subpackages)

        assert package.full_name == 'mypackage'
        assert package.name == 'mypackage'
        assert package.subgroups == subpackages
        assert package.assets == modules
        assert package.init_module is init_module
        assert package.deep_assets == [
            *modules,
            *sub_modules
        ]

class PythonApplicationTest:
    def test_init(self, mocker):
        entry_module = mocker.MagicMock(spec=PythonModule)
        module1 = mocker.MagicMock(spec=PythonModule)
        module2 = mocker.MagicMock(spec=PythonModule)
        modules = [entry_module, module1, module2]

        application = PythonApplication(entry_point=entry_module, modules=modules, packages={})

        assert application.entry_point is entry_module
        assert application.assets == modules
        assert application.deep_assets == modules
        assert application.subgroups == {}
