import unittest
import bolero


class BoleroTestCase(unittest.TestCase):

    def setUp(self):
        bolero.app.config['TESTING'] = True
        self.app = bolero.app
        self.client = bolero.app.test_client()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
