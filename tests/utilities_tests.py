# This script consists of unittests for shared utilities.py
import os
import unittest

from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from python_scripts.utilities import *

# Hardcode to dev env
env_file = find_dotenv(f'.env.dev')
load_dotenv(env_file)
local_aspace = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))

class TestClientLogin(unittest.TestCase):

    def test_default_connection(self):
        """Test using default connection info found in secrets.py"""
        self.assertIsInstance(local_aspace, ASnakeClient)

    def test_error_connection(self):
        """Test using garbage input for ASnakeAuthError return"""
        not_aspace = client_login("https://www.cnn.com", "garbage", "garbage")
        self.assertEqual(not_aspace, ASnakeAuthError)

class TestReadCSV(unittest.TestCase):

    def test_good_csv(self):
        test_subjects = read_csv(str(Path(f'./test_data/mergesubjects_testdata.csv')))
        self.assertIsNotNone(test_subjects)
        for row in test_subjects:
            self.assertIsInstance(row, dict)

    def test_bad_csv(self):
        test_subjects = read_csv(str(Path(f'./test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_subjects, None)

class TestCheckUrl(unittest.TestCase):

    def test_check_url(self):
        """Tests that an existing url returns True"""
        test_response = check_url('https://example.com')
        self.assertIsInstance(test_response, bool)
        self.assertTrue(test_response)

    def test_check_missing_url(self):
        """Tests that a broken url returns None"""
        test_response = check_url('https://www.si.edu/nothinghere') # A bad url
        self.assertIsNone(test_response)

if __name__ == "__main__":
    unittest.main(verbosity=2)
