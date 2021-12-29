from pathlib import Path, PosixPath, WindowsPath, PurePath

import yaml
from yaml import YAMLError

from snakepack.config import ConfigException
from snakepack.config.model import SnakepackConfig
from snakepack.config.types import PythonVersion, FullyQualifiedPythonName


def path_to_yaml(dumper, data):
    return dumper.represent_data(str(data))


def pythonversion_to_yaml(dumper, data):
    return dumper.represent_data(data.value)


def fqpn_to_yaml(dumper, data):
    return dumper.represent_data(str(data))


yaml.add_representer(PosixPath, path_to_yaml)
yaml.add_representer(WindowsPath, path_to_yaml)
yaml.add_representer(PythonVersion, pythonversion_to_yaml)
yaml.add_representer(FullyQualifiedPythonName, fqpn_to_yaml)


def parse_yaml_config(config: str) -> SnakepackConfig:
    try:
        config_dict = yaml.safe_load(config)
    except YAMLError as e:
        raise ConfigException('Configuration contains invalid YAML')

    return SnakepackConfig(**config_dict)


def generate_yaml_config(config: SnakepackConfig) -> str:
    config_dict = config.dict()
    yaml_config = yaml.dump(config_dict)

    return yaml_config