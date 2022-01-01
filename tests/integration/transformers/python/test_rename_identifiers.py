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
            x = 5;
            def foo(attr, anattr):
                pass
            def bar(attr, anattr):
                return b(attr, anattr)
            class Class(object):
                attr = 'foo'
            foo(x);
            y = 6
            a = x + y
            Class.attr = 'bar'
            def imported(a, b, c):
                o = True
                
                def inner():
                    nonlocal o
                    print(o)
            zigzag = 5
            zigzag = 6
            
            def function():
                zigzag = 0
            
            zigzag += 1
            """
        )

        expected_output_content = dedent(
            """
            a = 5;
            def b(a, b):
                pass
            def c(a, c):
                return b(a, c)
            class d(object):
                attr = 'foo'
            b(a);
            e = 6
            f = a + e
            d.attr = 'bar'
            def imported(a, b, c):
                d = True
                
                def e():
                    nonlocal d
                    print(d)
            g = 5
            g = 6
                  
            def h():
                a = 0
            
            g += 1
            """
        )

        self._test_transformation(
            input=input_content,
            expected_output=expected_output_content,
            options=RenameIdentifiersTransformer.Options(only_rename_in_local_scope=False)
        )

    def test_transform_only_rename_in_local_scope(self):
        input_content = dedent(
            """
            x = 5;
            def foo(attr, anattr):
                pass
            def bar(attr, anattr):
                return b(attr, anattr)
            class Class(object):
                attr = 'foo'
            foo(x);
            y = 6
            a = x + y
            Class.attr = 'bar'
            def imported(a, b, c):
                o = True

                def inner():
                    nonlocal o
                    print(o)
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
                
                def func2():
                    var2 = 2
                    
                    def func3():
                        print(var1 + var2)
            """
        )

        expected_output_content = dedent(
            """
            x = 5;
            def foo(attr, anattr):
                pass
            def bar(attr, anattr):
                return b(attr, anattr)
            class Class(object):
                attr = 'foo'
            foo(x);
            y = 6
            a = x + y
            Class.attr = 'bar'
            def imported(a, b, c):
                d = True
                
                def e():
                    nonlocal d
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
                
                def c():
                    d = 2
                    
                    def e():
                        print(b + d)
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

        import_graph_analysis = MagicMock(spec=ImportGraphAnalyzer.Analysis)
        import_graph_analysis.get_importing_modules.side_effect = _get_importing_modules
        import_graph_analyzer = MagicMock(spec=ImportGraphAnalyzer)
        import_graph_analyzer.analyse_assets.return_value = import_graph_analysis

        return [
            ScopeAnalyzer(),
            import_graph_analyzer
        ]