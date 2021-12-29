from unittest.mock import MagicMock

from libcst import Import, ImportAlias, Name, Attribute
from modulegraph.modulegraph import ModuleGraph, Node

from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.assets.python import PythonApplication, PythonModule


class ImportGraphAnalyzerAnalysisTest:
    def test_modulegraph_returns_no_referers(self):
        module_graph = MagicMock(spec=ModuleGraph)
        module_graph.getReferers.return_value = []
        application = MagicMock(spec=PythonApplication)
        node_map = MagicMock()
        import_metadata = MagicMock()

        test_imported_module = MagicMock(spec=PythonModule)

        analysis = ImportGraphAnalyzer.Analysis(
            module_graph=module_graph,
            asset_group=application,
            node_map=node_map,
            import_metadata=import_metadata
        )

        imported_modules = analysis.get_importing_modules(test_imported_module)

        assert imported_modules == []

    def test_without_identifier(self):
        module_graph = MagicMock(spec=ModuleGraph)
        node1 = MagicMock(spec=Node)
        node2 = MagicMock(spec=Node)
        node3 = MagicMock(spec=Node)
        module_graph.getReferers.return_value = [
            node1,
            node2
        ]
        application = MagicMock(spec=PythonApplication)
        module1 = MagicMock(spec=PythonModule)
        module2 = MagicMock(spec=PythonModule)
        test_imported_module = MagicMock(spec=PythonModule)

        node_map = {
            module1: node1,
            module2: node2,
            test_imported_module: node3
        }

        module1_imports = MagicMock()
        module2_imports = MagicMock()
        testmodule_imports = MagicMock()
        import_metadata = {
            module1: module1_imports,
            module2: module2_imports,
            test_imported_module: testmodule_imports
        }

        analysis = ImportGraphAnalyzer.Analysis(
            module_graph=module_graph,
            asset_group=application,
            node_map=node_map,
            import_metadata=import_metadata
        )

        imported_modules = analysis.get_importing_modules(test_imported_module)

        assert len(imported_modules) == 2
        assert module1 in imported_modules
        assert module2 in imported_modules

    def test_import_stmts(self):
        module_graph = MagicMock(spec=ModuleGraph)
        node1 = MagicMock(spec=Node)
        node2 = MagicMock(spec=Node)
        node3 = MagicMock(spec=Node)
        module_graph.getReferers.return_value = [
            node1,
            node2
        ]
        application = MagicMock(spec=PythonApplication)
        module1 = MagicMock(spec=PythonModule)
        module2 = MagicMock(spec=PythonModule)
        test_imported_module = MagicMock(spec=PythonModule)
        test_imported_module.full_name = 'testmodule'
        test_identifier = 'test'

        node_map = {
            module1: node1,
            module2: node2,
            test_imported_module: node3
        }

        module1_importstmt = MagicMock(spec=Import)

        module1_importalias1 = MagicMock(spec=ImportAlias)
        module1_importalias1_name = MagicMock(spec=Name)
        module1_importalias1_name.value = 'not_test'
        module1_importalias1.name = module1_importalias1_name

        module1_importalias2 = MagicMock(spec=ImportAlias)
        module1_importalias2_attr = MagicMock(spec=Attribute)
        module1_importalias2_attr_name = MagicMock(spec=Name)
        module1_importalias2_attr_name.value = 'testmodule'
        module1_importalias2_attr.attr = module1_importalias2_attr_name
        module1_importalias2.name = module1_importalias2_attr

        module1_importstmt.names = [
            module1_importalias1,
            module1_importalias2
        ]
        module1_imports = [
            module1_importstmt
        ]

        module2_importstmt = MagicMock(spec=Import)

        module2_importalias1 = MagicMock(spec=ImportAlias)
        module2_importalias1_name = MagicMock(spec=Name)
        module2_importalias1_name.value = 'foo'
        module2_importalias1.name = module2_importalias1_name

        module2_importalias2 = MagicMock(spec=ImportAlias)
        module2_importalias2_attr = MagicMock(spec=Attribute)
        module2_importalias2_attr_name = MagicMock(spec=Name)
        module2_importalias2_attr_name.value = 'bar'
        module2_importalias2_attr.attr = module2_importalias2_attr_name
        module2_importalias2.name = module2_importalias2_attr

        module2_importstmt.names = [
            module2_importalias1,
            module2_importalias2
        ]
        module2_imports = [
            module2_importstmt
        ]

        testmodule_imports = MagicMock()
        import_metadata = {
            module1: {
                ImportGraphAnalyzer.ImportProvider: module1_imports
            },
            module2: {
                ImportGraphAnalyzer.ImportProvider: module2_imports
            },
            test_imported_module: testmodule_imports
        }

        analysis = ImportGraphAnalyzer.Analysis(
            module_graph=module_graph,
            asset_group=application,
            node_map=node_map,
            import_metadata=import_metadata
        )

        imported_modules = analysis.get_importing_modules(test_imported_module, test_identifier)

        assert len(imported_modules) == 1
        assert module1 in imported_modules
        assert module2 not in imported_modules

    def test_importfrom_stmts(self):
        pass
