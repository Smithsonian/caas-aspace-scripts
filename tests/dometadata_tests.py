#!/usr/bin/env python

# This script consists of unittests for update_znames.py
import copy
import json
import unittest

from python_scripts.update_authorityids import *
from secrets import *
# from test_data.authorityids_testdata import *  TODO: change this


# class TestClientLogin(unittest.TestCase):
#
    # def test_default_connection(self):
    #     """Test using default connection info found in secrets.py"""
    #     self.local_aspace = client_login(as_api, as_un, as_pw)
    #     self.assertIsInstance(self.local_aspace, ASnakeClient)
    #
    # def test_error_connection(self):
    #     """Test using garbage input for ASnakeAuthError return"""
    #     self.local_aspace = client_login("https://www.cnn.com", "garbage", "garbage")
    #     self.assertEqual(self.local_aspace, ASnakeAuthError)


class TestReadCSV(unittest.TestCase):

    def test_good_csv(self):
        test_missinguris = read_csv(str(Path(f'../test_data/MissingTitles_BeGone.csv')))  # TODO: Change CSV to match
        self.assertIsNotNone(test_missinguris)
        self.assertIsInstance(test_missinguris[1], str)

    def test_bad_csv(self):
        test_missinguris = read_csv(str(Path(f'../test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_missinguris, None)


# class TestUpdateObject(unittest.TestCase):
#
#     def test_aspace_post_response(self):
#         self.local_aspace = client_login(as_api, as_un, as_pw)
#         pass
#
#     def test_bad_post(self):
#         self.local_aspace = client_login(as_api, as_un, as_pw)
#         pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
