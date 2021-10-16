from libcst import Module

from snakepack.assets import AssetType, AssetContent
from snakepack.assets.python import Python, PythonModule, PythonModuleCst, PythonPackage, PythonApplication


class PythonTest:
    def test_python_asset_type(self):
        assert issubclass(Python, AssetType)


class PythonModuleTest:
    def test_init(self, mocker):
        content = mocker.MagicMock(spec=AssetContent)
        module = PythonModule(full_name='some.test.module', content=content)

        assert module.full_name == 'some.test.module'
        assert module.name == 'module'
        assert module.content is content


class PythonModuleCstTest:
    def test_init(self, mocker):
        cst = mocker.MagicMock(spec=Module)
        cst.code = 'x=5'
        content = PythonModuleCst(cst=cst)

        assert content.cst is cst
        assert str(content) == 'x=5'


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
        assert package.subpackages == subpackages
        assert package.modules == modules
        assert package.init_module is init_module
        assert package.assets == modules

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
        assert package.subpackages == subpackages
        assert package.modules == modules
        assert package.init_module is init_module
        assert package.assets == [
            *modules,
            *sub_modules
        ]


class PythonApplicationTest:
    def test_init(self, mocker):
        entry_module = mocker.MagicMock(spec=PythonModule)
        module1 = mocker.MagicMock(spec=PythonModule)
        module2 = mocker.MagicMock(spec=PythonModule)
        modules = [entry_module, module1, module2]

        application = PythonApplication(entry_point=entry_module, modules=modules)

        assert application.entry_point is entry_module
        assert application.modules == modules
        assert application.assets == modules
