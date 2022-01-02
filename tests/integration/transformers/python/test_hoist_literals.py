from textwrap import dedent
from typing import Iterable

import pytest
from libcst import parse_module

from snakepack.analyzers import Analyzer
from snakepack.analyzers.python.literals import LiteralDuplicationAnalyzer
from snakepack.analyzers.python.scope import ScopeAnalyzer
from snakepack.assets.python import PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers.python.hoist_literals import HoistLiteralsTransformer
from tests.integration.transformers.python._base import PythonModuleCstTransformerIntegrationTestBase


class HoistLiteralsTransformerIntegrationTest(PythonModuleCstTransformerIntegrationTestBase):
    _TRANSFORMER_CLASS = HoistLiteralsTransformer

    def test_transform(self):
        input_content = dedent(
            """
            \"\"\" module doc \"\"\"
            from __future__ import annotations; from __future__ import absolute_import
            from __future__ import division
            foo('some_long_string', x['some_long_string'])
            bar('some_long_string')
            foo('s', x['s'])
            foo('r', 'r', 'r')
            x = 'assigned'
            foo('assigned', 'assigned', 'assigned')
            bar('hello', 'hello', 'hello')
            z = 'hello'
            p = 'test'
            def test():
                o = 'nope'
            def func(a, b):
                print(p)
                print('nope')
                
            def test():
                a = False
                b = False
                print('some_very_long_string')
                print('some_very_long_string')
                
            print('again_some_very_long_string')
            print('again_some_very_long_string')
            
            def other_test():
                a = False
                print('some_very_long_string')
                print('some_very_long_string')

            """
        )

        expected_output_content = dedent(
            """
            \"\"\" module doc \"\"\"
            from __future__ import annotations; from __future__ import absolute_import
            from __future__ import division
            a='some_long_string'; b='r'; c='hello'; d='nope'; e='some_very_long_string'; f='again_some_very_long_string'; foo(a, x[a])
            bar(a)
            foo('s', x['s'])
            foo(b, b, b)
            x = 'assigned'
            foo(x, x, x)
            bar(c, c, c)
            z = c
            p = 'test'
            def test():
                o = d
            def func(a, b):
                print(p)
                print(d)
                
            def test():
                a = False
                b = False
                print(e)
                print(e)
                
            print(f)
            print(f)
      
            def other_test():
                a = False
                print(e)
                print(e)

            """
        )

        self._test_transformation(input=input_content, expected_output=expected_output_content)

    def _create_analyzers(self) -> Iterable[Analyzer]:
        return [
            LiteralDuplicationAnalyzer(),
            ScopeAnalyzer()
        ]