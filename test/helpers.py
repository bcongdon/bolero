import unittest
import bolero


class BoleroTestCase(unittest.TestCase):

    def setUp(self):
        bolero.app.config['TESTING'] = True
        bolero.setup()
        self.app = bolero.app
        self.client = bolero.app.test_client()

    def tearDown(self):
        pass
