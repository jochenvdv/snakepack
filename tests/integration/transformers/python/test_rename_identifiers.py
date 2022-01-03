from textwrap import dedent
from typing import Iterable
from unittest.mock import MagicMock

from libcst import parse_module

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.imports import ImportGraphAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.rename_identifiers import RenameIdentifiersTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class RenameIdentifiersTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = RenameIdentifiersTransformer

    def test_transform(self):
        input_content = dedent(
            """
            xo = 5;
            def foo(attr, anattr):
                pass
            def bar(attr, anattr):
                return b(attr, anattr)
            class Class(object):
                attr = 'foo'
            foo(x);
            yo = 6
            a = xo + yo
            Class.attr = 'bar'
            def imported(a, b, c):
                ooops = True
                
                def inner():
                    nonlocal ooops
                    print(ooops)
            zigzag = 5
            zigzag = 6
            
            def function():
                zigzag = 0
            
            zigzag += 1
            """
        )

        expected_output_content = dedent(
            """       
            b = 5;
            def c(d, e):
                pass
            def d(e, f):
                return b(e, f)
            class e(object):
                attr = 'foo'
            c(x);
            f = 6
            a = b + f
            e.attr = 'bar'
            def imported(a, b, c):
                j = True
            
                def g():
                    nonlocal j
                    print(j)
            h = 5
            h = 6
            
            def g():
                h = 0
            
            h += 1
            """
        )

        self._test_transformation(
            input=input_content,
            expected_output=expected_output_content,
            options=RenameIdentifiersTransformer.Options(only_rename_locals=False)
        )

    def test_transform_only_rename_in_local_scope(self):
        input_content = dedent(
            """
            xo = 5;
            def foo(attr: int, anattr):
                pass
            def bar(attr, anattr: str):
                return b(attr, anattr)
            class Class(object):
                attr = 'foo'
            foo(x);
            yo = 6
            a = xo + yo
            Class.attr = 'bar'
            def imported(a, b, c):
                ooops = True

                def inner():
                    nonlocal ooops
                    nonlocal c
                    print(ooops)
            zigzag = 5
            zigzag = 6

            def function():
                zigzag = 0

            zigzag += 1
            
            def nonlocal_1():
                foobar = True
                
                def nonlocal_2():
                    nonlocal foobar
                    foobar = False
            
            def func1():
                var1 = 1
                
                def func2(some_var: SomeClazz):
                    var2 = 2
                    print(some_var)
                    some_var = 'reassigned'
                    
                    def func3(other_var):
                        print(var2=some_var)
                        print(other_var)
                        print(var1 + var2)
            
            def importtest():
                imported_var: SomeType
                
                from some_module import imported_var
            """
        )

        expected_output_content = dedent(
            """
            xo = 5;
            def foo(attr: int, anattr):
                pass
            def bar(attr, anattr: str):
                return b(attr, anattr)
            class Class(object):
                attr = 'foo'
            foo(x);
            yo = 6
            a = xo + yo
            Class.attr = 'bar'
            def imported(a, b, c):
                d = True
                
                def e():
                    nonlocal d
                    nonlocal c
                    print(d)
            zigzag = 5
            zigzag = 6
            
            def function():
                b = 0
            
            zigzag += 1
            
            def nonlocal_1():
                b = True
                
                def c():
                    nonlocal b
                    b = False
                          
            def func1():
                b = 1
                
                def c(some_var: SomeClazz):
                    d = 2
                    print(some_var)
                    some_var = 'reassigned'

                    def e(other_var):
                        print(var2=some_var)
                        print(other_var)
                        print(b + d)
            
            def importtest():
                imported_var: SomeType
                
                from some_module import imported_var
            """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)

    def _create_analyzers(self) -> Iterable[Analyzer]:
        def _get_importing_modules(module, identifier):
            if identifier == 'imported':
                return [
                    MagicMock()
                ]

            return []

        def _identifier_imported_in_module(identifier, module):
            if identifier == 'imported_var':
                return True

            return False

        import_graph_analysis = MagicMock(spec=ImportGraphAnalyzer.Analysis)
        import_graph_analysis.get_importing_modules.side_effect = _get_importing_modules
        import_graph_analysis.identifier_imported_in_module.side_effect = _identifier_imported_in_module
        import_graph_analyzer = MagicMock(spec=ImportGraphAnalyzer)
        import_graph_analyzer.analyse_assets.return_value = import_graph_analysis

        return [
            ScopeAnalyzer(),
            import_graph_analyzer
        ]