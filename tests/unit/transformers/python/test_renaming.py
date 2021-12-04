import string

from libcst.metadata import Scope

from snakepack.transformers.python._renaming import NameRegistry


class NameRegistryTest:
    def test_init(self):
        registry = NameRegistry()

    def test_generate_name(self, mocker):
        registry = NameRegistry()
        scope = mocker.MagicMock(spec=Scope)

        expected = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        ]

        for i in range(200):
            name = registry.generate_name_for_scope(scope=scope)
            assert not name.startswith(string.digits)

            if i < 52:
                assert name == expected[i]
            elif i == 105:
                assert name == 'a2'
            elif i == 176:
                assert name == 'cd'

            registry.register_name_for_scope(scope=scope, name=name)

    def test_generate_name_and_dont_use(self, mocker):
        registry = NameRegistry()
        scope = mocker.MagicMock(spec=Scope)

        name = registry.generate_name_for_scope(scope=scope)
        second_name = registry.generate_name_for_scope(scope=scope)
        registry.register_name_for_scope(scope=scope, name=second_name)
        third_name = registry.generate_name_for_scope(scope=scope)

        assert name == third_name