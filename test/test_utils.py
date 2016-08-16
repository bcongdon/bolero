from helpers import BoleroTestCase
from bolero.utils import requires


class UtilsTest(BoleroTestCase):

    def test_requires_decorator(self):
        self.app.config['AUTH_KEYS']['test.key'] = "12345"

        @requires('test.key')
        def simple_api(config):
            assert config['test.key'] == '12345'
        simple_api()
