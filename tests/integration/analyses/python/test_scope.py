from textwrap import dedent

from libcst import parse_module
from libcst.metadata import FunctionScope

from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst, PythonModule


class ScopeAnalysisIntegrationTest:
    def test_analyze(self):
        content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    a = True
                    
                    def b(c):
                        return c
                        
                    class D:
                        e = True
                        
                        def f(g):
                            return g
                    """
                )
            )
        )
        module = PythonModule(
            full_name='a',
            content=content,
            source=None
        )

        analyzer = ScopeAnalyzer()
        analysis = analyzer.analyse(module)

        g_var = content.cst.body[2].body.body[1].body.body[0].body[0].value

        assert isinstance(analysis[module][g_var], FunctionScope)
        assert analysis[module][g_var]
