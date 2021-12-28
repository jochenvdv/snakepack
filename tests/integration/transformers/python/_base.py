from abc import abstractmethod
from textwrap import dedent
from typing import Optional, Iterable

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesmith import from_grammar
from libcst import parse_module

from snakepack.analyzers import Analyzer
from snakepack.analyzers._base import SubjectAnalyzer
from snakepack.assets import AssetContent, Asset
from snakepack.assets.python import PythonModule, PythonModuleCst
from snakepack.config.model import GlobalOptions
from snakepack.transformers import Transformer
from snakepack.transformers.python._base import PythonModuleTransformer


class PythonModuleCstTransformerIntegrationTestBase:
    _TRANSFORMER_CLASS = NotImplemented

    _EXCLUDED_EXAMPLES = {
        '\n \x0cpass#',
        '\n\\\n#'
    }

    @pytest.mark.hypothesis
    @settings(suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.filter_too_much
    ])
    @given(input=from_grammar().filter(lambda x: x not in PythonModuleCstTransformerIntegrationTestBase._EXCLUDED_EXAMPLES))
    def test_randomly_generated_code(self, input):
        transformer = self._create_transformer()
        analyzers = self._create_analyzers()

        self._test_transformation(
            transformer=transformer,
            input=input,
            expected_output=None,
            analyzers=analyzers
        )

    def _create_transformer(self) -> PythonModuleTransformer:
        global_options = GlobalOptions()
        transformer = self._TRANSFORMER_CLASS(global_options=global_options)
        return transformer

    def _create_analyzers(self) -> Iterable[Analyzer]:
        return []

    def _test_transformation(
            self,
            input: str,
            expected_output: Optional[str] = None,
            transformer: Optional[PythonModuleTransformer] = None,
            analyzers: Optional[Iterable[Analyzer]] = None
    ):
        input_content = PythonModuleCst(cst=parse_module(input))

        if expected_output is not None:
            expected_output = PythonModuleCst(cst=parse_module(dedent(expected_output)))

        if transformer is None:
            transformer = self._create_transformer()

        if analyzers is None:
            analyzers = self._create_analyzers()

        # analysis
        subject = PythonModule(full_name='test', content=input_content, source=None)
        analyses = {}

        for analyzer in analyzers:
            if isinstance(analyzer, SubjectAnalyzer):
                analysis = analyzer.analyse_subject(subject)
            else:
                analysis = analyzer.analyse()

            analyses[analyzer.__class__] = analysis

        # initial transformation
        output_first_pass = transformer.transform(analyses=analyses, subject=subject)

        assert output_first_pass.content is not input_content, 'Transformer output is same object as input'

        if expected_output is not None:
            assert str(output_first_pass.content) == str(expected_output), 'Transformer output doesn\'t match expected output'

        assert len(str(output_first_pass.content)) <= len(str(input)), 'Transformer output is larger than input'

        try:
            compile(
                source=str(output_first_pass.content),
                filename='<string>',
                mode='exec'
            )
        except SyntaxError as e:
            pytest.fail('Transformer output contains syntax errors')

        # second transformation on original input
        subject = PythonModule(full_name='test', content=input_content, source=None)

        for analyzer in analyzers:
            if isinstance(analyzer, SubjectAnalyzer):
                analysis = analyzer.analyse_subject(subject)
            else:
                analysis = analyzer.analyse()

            analyses[analyzer.__class__] = analysis

        output_second_pass = transformer.transform(analyses=analyses, subject=subject)
        assert str(output_second_pass.content) == str(output_first_pass.content), 'Transformer isn\'t idempotent'

        # second transformation on output of initial transformation
        subject = PythonModule(full_name='test', content=output_second_pass.content, source=None)

        for analyzer in analyzers:
            if isinstance(analyzer, SubjectAnalyzer):
                analysis = analyzer.analyse_subject(subject)
            else:
                analysis = analyzer.analyse()

            analyses[analyzer.__class__] = analysis

        output_third_pass = transformer.transform(analyses=analyses, subject=subject)
        assert str(output_third_pass.content) == str(output_second_pass.content), 'Transformer output is not fully transformed'

