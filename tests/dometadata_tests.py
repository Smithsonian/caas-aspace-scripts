#!/usr/bin/env python

# This script consists of unittests for update_znames.py
import copy
import json
import contextlib
import io
import unittest

from python_scripts.delete_dometadata import *
from test_data.dometadata_testdata import *
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

    def test_get_digobjs_all(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_archivesspace.get_repo_info()
        test_digitalobjects = test_archivesspace.get_digitalobjects(test_archivesspace.repo_info[1]['uri'],
                                                                    ('all_ids', True))
        self.assertIsInstance(test_digitalobjects, list)
        self.assertIsNot(len(test_digitalobjects), 0)
        self.assertIsInstance(test_digitalobjects[0], int)

    def test_get_digobjs_page(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_archivesspace.get_repo_info()
        test_digitalobjects = test_archivesspace.get_digitalobjects(test_archivesspace.repo_info[1]['uri'],
                                                                    ('page', 1))
        self.assertIsInstance(test_digitalobjects, dict)
        self.assertIsNot(len(test_digitalobjects), 0)
        self.assertIs(test_digitalobjects['first_page'], 1)

    def test_get_digobjs_set(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_archivesspace.get_repo_info()
        id_set_values = r'18&id_set=20'
        test_digitalobjects = test_archivesspace.get_digitalobjects(test_archivesspace.repo_info[1]['uri'],
                                                                    ('id_set', id_set_values))
        self.assertIsInstance(test_digitalobjects, list)
        self.assertIsNot(len(test_digitalobjects), 0)
        self.assertIs(type(test_digitalobjects[0]), dict)

    def test_get_digobj(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_do_json = test_archivesspace.get_digitalobject(test_digital_object_repo_uri, test_digital_object_id)
        self.assertIsInstance(test_do_json, dict)
        self.assertEqual(test_do_json['digital_object_id'], test_digital_object_user_identifier)

    def test_bad_digobj(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            test_do_json = test_archivesspace.get_digitalobject(test_digital_object_repo_uri, 10000000000000000)
            print(test_do_json)
        self.assertTrue(r"""get_digitalobject() - Unable to retrieve digital object with provided URI: {'error': 'DigitalObject not found'}""" in f.getvalue())




class TestReadCSV(unittest.TestCase):

    def test_good_csv(self):
        test_missinguris = read_csv(str(Path(f'../test_data/MissingTitles_BeGone.csv')))  # TODO: Change CSV to match
        self.assertIsNotNone(test_missinguris)
        self.assertIsInstance(test_missinguris[1], str)

    def test_bad_csv(self):
        test_missinguris = read_csv(str(Path(f'../test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_missinguris, None)


class TestRecordError(unittest.TestCase):

    def test_str_input(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            record_error('This is a test error', 'Error 404 - page not found')
        self.assertTrue(r"""This is a test error: Error 404 - page not found""" in f.getvalue())

    def test_tuple_input(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            record_error('This is a test error', ('test_this', 'and_this'))
        self.assertTrue(r"""This is a test error: ('test_this', 'and_this')""" in f.getvalue())

    def test_bool_input(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            record_error('This is a test error', False)
        self.assertTrue(r"""This is a test error: False""" in f.getvalue())

class TestParseDeleteFields(unittest.TestCase):

    def test_delete_dates(self):
        deleted_dates_json = parse_delete_fields(test_digital_object_dates)
        self.assertIs(len(deleted_dates_json['dates']), 0)
        self.assertIsInstance(deleted_dates_json['dates'], list)


class TestDeleteFieldInfo(unittest.TestCase):

    def test_delete_dates(self):
        deleted_dates_json = delete_field_info(test_digital_object_dates, 'dates')
        self.assertIs(len(deleted_dates_json['dates']), 0)
        self.assertIsInstance(deleted_dates_json['dates'], list)

    def test_delete_notes(self):
        pass


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
