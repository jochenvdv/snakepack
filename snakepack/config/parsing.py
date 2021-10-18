import yaml
from yaml import YAMLError

from snakepack.config import ConfigException
from snakepack.config.model import SnakepackConfig


def parse_yaml_config(config: str) -> SnakepackConfig:
    try:
        config_dict = yaml.safe_load(config)
    except YAMLError as e:
        raise ConfigException('Configuration contains invalid YAML')

    return SnakepackConfig(**config_dict)