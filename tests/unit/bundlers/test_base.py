from snakepack.bundlers import Bundle


class BundleTest:
    def test_init(self):
        bundle = Bundle(name='bundle1')

        assert bundle.name == 'bundle1'
