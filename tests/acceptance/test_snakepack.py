import pytest

from snakepack.app import snakepack


class SnakepackAcceptanceTest:
    @pytest.mark.skip
    def test_compile_snakepack_as_application(self, cli_runner):
        result = cli_runner.invoke(snakepack, args=[])
        print(result.output)

        assert result.exit_code == 0, 'Initial compilation failed'
