import pytest
from yaml import YAMLError

from snakepack.config import ConfigException
from snakepack.config.model import SnakepackConfig
from snakepack.config.parsing import parse_yaml_config


class ParseYamlConfigTest:
    def test_returns_parsed_config(self, mocker):
        safe_load_mock = mocker.patch('yaml.safe_load')
        safe_load_mock.return_value = {}

        yaml_config = ''
        config = parse_yaml_config(yaml_config)

        assert isinstance(config, SnakepackConfig)
        safe_load_mock.assert_called_once_with(yaml_config)

    def test_throws_config_exception_if_yaml_invalid(self, mocker):
        safe_load_mock = mocker.patch('yaml.safe_load')
        safe_load_mock.side_effect = YAMLError()

        with pytest.raises(ConfigException) as e:
            yaml_config = ''
            config = parse_yaml_config(yaml_config)

            safe_load_mock.assert_called_once_with(yaml_config)
