from typing import Optional, Iterable

import pytest

from snakepack.analyzers import Analyzer
from snakepack.assets import AssetContent, Asset
from snakepack.assets.python import PythonModule
from snakepack.transformers import Transformer


class PythonModuleCstTransformerIntegrationTestBase:
    def _test_transformation(self, transformer: Transformer, input: AssetContent, expected_output: AssetContent, analyzers: Optional[Iterable[Analyzer]] = None):
        # analysis
        subject = PythonModule(full_name='test', content=input, source=None)
        analyses = {}

        if analyzers is not None:
            for analyzer in analyzers:
                analysis = analyzer.analyse(subject)
                analyses[analyzer.__class__] = analysis

        # initial transformation
        output_first_pass = transformer.transform(analyses=analyses, subject=subject)

        assert output_first_pass.content is not input, 'Transformer output is same object as input'
        assert str(output_first_pass.content) == str(expected_output), 'Transformer output doesn\'t match expected output'
        assert len(str(output_first_pass.content)) < len(str(input)), 'Transformer output is larger than input'


        try:
            compile(
                source=str(output_first_pass.content),
                filename='<string>',
                mode='exec'
            )
        except SyntaxError as e:
            pytest.fail('Transformer output contains syntax errors')

        # second transformation on original input
        subject = PythonModule(full_name='test', content=input, source=None)

        if analyzers is not None:
            for analyzer in analyzers:
                analysis = analyzer.analyse(subject)
                analyses[analyzer.__class__] = analysis

        output_second_pass = transformer.transform(analyses=analyses, subject=subject)
        assert str(output_second_pass.content) == str(output_first_pass.content), 'Transformer isn\'t idempotent'

        # second transformation on output of initial transformation
        subject = PythonModule(full_name='test', content=output_second_pass.content, source=None)

        if analyzers is not None:
            for analyzer in analyzers:
                analysis = analyzer.analyse(subject)
                analyses[analyzer.__class__] = analysis

        output_third_pass = transformer.transform(analyses=analyses, subject=subject)
        assert str(output_third_pass.content) == str(output_second_pass.content), 'Transformer output is not fully transformed'

