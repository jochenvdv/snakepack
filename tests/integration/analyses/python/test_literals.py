from textwrap import dedent

from libcst import parse_module
from libcst.metadata import FunctionScope

from snakepack.analyzers.python.literals import LiteralDuplicationAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst, PythonModule


class LiteralDuplicationAnalyzerIntegrationTest:
    def test_analyze(self):
        content = PythonModuleCst(
            cst=parse_module(
                dedent(
                    """
                    a = 'foo'
                    b: str = 'foo'
                    b += 'invalidate'
                    c = 'foo'
                    c += ''
                    d = 'foo'
                    d: str = 'foo'
                    e = 'foo'
                    e = 'not anymore'
                    
                    x = 'bar'
                    y('bar', 'bar', 'bar')
                    """
                )
            )
        )
        module = PythonModule(
            full_name='a',
            content=content,
            source=None
        )

        analyzer = LiteralDuplicationAnalyzer()
        analysis = analyzer.analyse(module)

        foo_node = content.cst.body[0].body[0].value
        foo_assignments = analysis.get_preceding_assignments(module, foo_node)

        assert len(foo_assignments) == 1
        assert 'a' in foo_assignments
        assert len(foo_assignments['a']) == 1

        bar_node = content.cst.body[9].body[0].value
        bar_assignments = analysis.get_preceding_assignments(module, bar_node)

        assert len(bar_assignments) == 1
        assert 'x' in bar_assignments
        assert len(bar_assignments['x']) == 1
