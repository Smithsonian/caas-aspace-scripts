#!/usr/bin/env python

# This script consists of unittests for update_znames.py
import copy
import json
import contextlib
import io
import unittest

from python_scripts.delete_dometadata import *
from secrets import *
# from test_data.authorityids_testdata import *  TODO: change this


class TestArchivesSpaceClass(unittest.TestCase):

    def test_asnake_connection(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        self.assertIsInstance(test_archivesspace.aspace_client, ASnakeClient)

    def test_bad_connection(self):
        with self.assertRaises(ASnakeAuthError):
            ArchivesSpace(as_api_stag, "bad_user", "bad_password")

    def test_get_repoinfo(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        repos_info = test_archivesspace.get_repo_info()
        self.assertIsInstance(repos_info, list)
        self.assertIn('uri', repos_info[1].keys())

    def test_get_digobj_all(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_archivesspace.get_repo_info()
        test_digitalobjects = test_archivesspace.get_digitalobjects(test_archivesspace.repo_info[1]['uri'],
                                                                    ('all_ids', True))
        print(test_digitalobjects)

    def test_get_digobj_page(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_archivesspace.get_repo_info()
        test_digitalobjects = test_archivesspace.get_digitalobjects(test_archivesspace.repo_info[1]['uri'],
                                                                    ('page', 1))
        print(test_digitalobjects)

    def test_get_digobj_set(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_archivesspace.get_repo_info()
        id_set_values = r'18&id_set=20'
        test_digitalobjects = test_archivesspace.get_digitalobjects(test_archivesspace.repo_info[1]['uri'],
                                                                    ('id_set', id_set_values))
        print(test_digitalobjects)





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
