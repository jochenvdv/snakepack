from snakepack.config import Options, ComponentConfig, ConfigurableComponent


class ConfigurableComponentTest:
    class TestComponentA(ConfigurableComponent):
        pass

    class TestComponentB(ConfigurableComponent):
        class Options(Options):
            test: bool = True

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


class ComponentConfigTest:
    def test_init(self):
        config = ComponentConfig(name='test_component')

    def test_init_with_options(self, mocker):
        options = mocker.MagicMock(spec=Options)
        config = ComponentConfig(name='test_component', options=options)


class OptionsTest:
    def test_init(self):
        options = Options()
