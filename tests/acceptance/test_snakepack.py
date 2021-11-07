from snakepack.app import snakepack


class SnakepackAcceptanceTest:
    def test_compile_self(self, cli_runner):
        result = cli_runner.invoke(snakepack, args=[])
        print(result.output)

        assert result.exit_code == 0, 'Initial compilation failed'
