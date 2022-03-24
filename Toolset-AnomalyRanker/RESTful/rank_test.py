import os
import unittest

import ranker_app


# Configuration paths.
THIS_DIRECTORY_PATH = os.path.dirname(os.path.abspath(__file__))
GML_FILE_PATH = os.path.join(THIS_DIRECTORY_PATH, 'resources/ic.gml')


class RankTest(unittest.TestCase):
    def setUp(self):
        self.__client = ranker_app.app.test_client()
        with open(GML_FILE_PATH, mode='r') as gml_file:
            gml_string = gml_file.read()
        self.__data = {
            'gml': gml_string,
        }

    def test_rank(self):
        response = self.__client.post('/rank', json=self.__data)
        # print(response.data)
