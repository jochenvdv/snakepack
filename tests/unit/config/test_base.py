import pytest
from pydantic import ValidationError

from snakepack.config import Options, ComponentConfig, ConfigurableComponent, ConfigException


class ConfigurableComponentTest:
    class TestComponentA(ConfigurableComponent):
        __config_name__ = 'test_component_a'

    class TestComponentB(ConfigurableComponent):
        class Options(Options):
            test: bool = True

        __config_name__ = 'test_component_b'

    def test_init(self):
        component = self.TestComponentA()

        assert isinstance(component.options, ConfigurableComponent.Options)

    def test_init_with_options(self):
        options = self.TestComponentA.Options()
        component = self.TestComponentA(options=options)

        assert component.options is options

    def test_init_options_defined(self):
        component = self.TestComponentB()

    def test_init_options_defined_and_passed(self):
        options = self.TestComponentB.Options(test=False)
        component = self.TestComponentB(options=options)

        assert component.options is options

    def test_component_types(self):
        assert ConfigurableComponent.__component_types__['test_component_a'] is self.TestComponentA
        assert ConfigurableComponent.__component_types__['test_component_b'] is self.TestComponentB


class ComponentConfigTest:
    class TestComponentX(ConfigurableComponent):
        __config_name__ = 'test_component_x'

        class Options(Options):
            test: bool

    class TestComponentY(ConfigurableComponent):
        __config_name__ = 'test_component_y'

        class Options(Options):
            pass

    def test_init(self):
        config = ComponentConfig(name='test_component_y')

    def test_init_missing_options(self):
        with pytest.raises(ValidationError):
            config = ComponentConfig(name='test_component_x')

    def test_init_unknown_component(self):
        with pytest.raises(ValidationError):
            config = ComponentConfig(name='test_component_z')

    def test_init_with_options_object(self, mocker):
        options = self.TestComponentX.Options(test=False)
        config = ComponentConfig(name='test_component_x', options=options)

    def test_init_with_options_dict(self, mocker):
        options = {'test': False}
        config = ComponentConfig(name='test_component_x', options=options)

    def test_initialize_component(self):
        options = self.TestComponentX.Options(test=False)
        config = ComponentConfig(name='test_component_x', options=options)

        component = config.initialize_component()

        assert isinstance(component, self.TestComponentX)
        assert component.options is options

class OptionsTest:
    def test_init(self):
        options = Options()