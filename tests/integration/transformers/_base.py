from snakepack.assets import AssetContent, Asset
from snakepack.transformers import Transformer


class TransformerIntegrationTestBase:
    def _test_transformation(self, transformer: Transformer, input: AssetContent, expected_output: AssetContent):
        # initial transformation
        output_first_pass = transformer.transform(content=input)
        print(output_first_pass)
        assert output_first_pass is not input, 'Transformer output is same object as input'
        assert str(output_first_pass) == str(expected_output), 'Transformer output doesn\'t match expected output'
        assert len(str(output_first_pass)) < len(str(input)), 'Transformer output is larger than input'
        """compile(
            source=str(output_first_pass),
            filename='<string>',
            mode='exec'
        )"""

        # second transformation on original input
        output_second_pass = transformer.transform(content=input)
        assert str(output_second_pass) == str(output_first_pass), 'Transformer isn\'t idempotent'

        # second transformation on output of initial transformation
        output_third_pass = transformer.transform(content=output_second_pass)
        assert str(output_third_pass) == str(output_second_pass), 'Transformer output is not fully transformed'

