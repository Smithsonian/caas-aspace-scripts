#!/usr/bin/env python

# This script consists of unittests for update_znames.py
import unittest

from python_scripts.one_time_scripts.update_authorityids import *


# from test_data.authorityids_testdata import *


class TestArchivesSpaceClass(unittest.TestCase):

    def test_client_variables(self):
        aspace_class = ArchivesSpace(2)
        self.assertIsInstance(aspace_class, ArchivesSpace)

    def test_client_fail(self):
        fail_aspace = ArchivesSpace(2)
        fail_aspace.aspace_client = ASnakeClient(baseurl="https://cnn.com", username="failure", password="failure")
        print(fail_aspace)
        with self.assertRaises(ASnakeAuthError) as context:
            print(context)
            fail_aspace.aspace_client = ASnakeClient(baseurl="https://cnn.com", username="failure", password="failure")

    def test_getobjectmetadata(self):
        pass


# class TestClientLogin(unittest.TestCase):
#
#     def test_default_connection(self):
#         """Test using default connection info found in secrets.py"""
#         self.local_aspace = client_login(as_api, as_un, as_pw)
#         self.assertIsInstance(self.local_aspace, ASnakeClient)
#
#     def test_error_connection(self):
#         """Test using garbage input for ASnakeAuthError return"""
#         self.local_aspace = client_login("https://www.cnn.com", "garbage", "garbage")
#         self.assertEqual(self.local_aspace, ASnakeAuthError)


class TestReadCSV(unittest.TestCase):

    def test_good_csv(self):
        test_ids = read_csv(str(Path('../test_data/resource_accession_IDs_all.csv')))
        self.assertIsNotNone(test_ids)
        for row in test_ids:
            self.assertIsInstance(row, dict)

    def test_bad_csv(self):
        test_ids = read_csv(str(Path('../test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_ids, None)


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
