import unittest
import bolero
from bolero import app


class BoleroTestCase(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        bolero.app.setup()
        self.app = app.app
        self.client = app.app.test_client()

    def tearDown(self):
        pass
