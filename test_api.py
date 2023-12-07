import json
import unittest

from main import api as api

# Open JSON test files
with open('data/real_time.json') as realtime_data_file:
    realtime_data_json = realtime_data_file.read()

with open('data/token.json') as token_data_file:
    token_data_json = token_data_file.read()

class TestApi(unittest.TestCase):
    
    def test_get_token(self):
        self.assertEqual(api.get_token(token_data_json), \
                         "e3afd8f9-a989-48db-86c6-6d3075d4071f")
        
    def test_get_data(self):
        self.assertIsNotNone(api.get_data(realtime_data_json))

    def test_get_timestamp(self):
        self.assertEqual(api.get_timestamp(realtime_data_json), "2023-04-27 19:02:16")

    def test_slice_data(self):
        pass

    def test_check_connection(self):
        pass


if __name__ == '__main__':
    unittest.main()