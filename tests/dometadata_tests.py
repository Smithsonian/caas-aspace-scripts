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
        test_digitalobjects = test_archivesspace.get_objects(test_archivesspace.repo_info[1]['uri'],
                                                             test_record_type,
                                                             ('all_ids', True))
        self.assertIsInstance(test_digitalobjects, list)
        self.assertIsNot(len(test_digitalobjects), 0)
        self.assertIsInstance(test_digitalobjects[0], int)

    def test_get_digobjs_page(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_archivesspace.get_repo_info()
        test_digitalobjects = test_archivesspace.get_objects(test_archivesspace.repo_info[1]['uri'],
                                                             test_record_type,
                                                             ('page', 1))
        self.assertIsInstance(test_digitalobjects, dict)
        self.assertIsNot(len(test_digitalobjects), 0)
        self.assertIs(test_digitalobjects['first_page'], 1)

    def test_get_digobjs_set(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_archivesspace.get_repo_info()
        id_set_values = r'18&id_set=20'
        test_digitalobjects = test_archivesspace.get_objects(test_archivesspace.repo_info[1]['uri'],
                                                             test_record_type,
                                                             ('id_set', id_set_values))
        self.assertIsInstance(test_digitalobjects, list)
        self.assertIsNot(len(test_digitalobjects), 0)
        self.assertIs(type(test_digitalobjects[0]), dict)

    def test_get_digobj(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        test_do_json = test_archivesspace.get_object(test_record_type,
                                                     test_object_id,
                                                     test_object_repo_uri)
        self.assertIsInstance(test_do_json, dict)
        self.assertEqual(test_do_json['digital_object_id'], test_object_user_identifier)

    def test_bad_digobj(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            test_archivesspace.get_object(test_record_type,
                                          10000000000000000,
                                          test_object_repo_uri)

        self.assertTrue(
            r"""get_object() - Unable to retrieve object with provided URI: {'error': 'DigitalObject not found'}""" in f.getvalue())

    def test_aspace_post_response(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        original_object_json = test_archivesspace.get_object(test_record_type,
                                                             test_object_id,
                                                             test_object_repo_uri)
        test_response = test_archivesspace.update_object(original_object_json['uri'],
                                                         original_object_json)
        self.assertEqual(test_response['status'], 'Updated')
        self.assertEqual(test_response['warnings'], [])

    def test_bad_post(self):
        test_archivesspace = ArchivesSpace(as_api_stag, as_un, as_pw)
        original_object_json = test_archivesspace.get_object(test_record_type,
                                                             test_object_id,
                                                             test_object_repo_uri)
        original_object_json['uri'] = 'laksjdlfieklkjfa'
        test_response = test_archivesspace.update_object(original_object_json['uri'],
                                                         original_object_json)
        self.assertIn('error', test_response)


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


# class TestReadCSV(unittest.TestCase):
#
#     def test_good_csv(self):
#         test_missinguris = read_csv(str(Path(f'../test_data/MissingTitles_BeGone.csv')))
#         self.assertIsNotNone(test_missinguris)
#         self.assertIsInstance(test_missinguris[1], str)
#
#     def test_bad_csv(self):
#         test_missinguris = read_csv(str(Path(f'../test_data/fake.csv')))
#         self.assertRaises(FileNotFoundError)
#         self.assertEqual(test_missinguris, None)


class TestParseDeleteFields(unittest.TestCase):

    def test_delete_single_date(self):
        modified_do_dates = deepcopy(test_digital_object_dates)
        modified_do_dates['dates'].pop(1)  # remove the digitized date
        test_fields_to_delete = parse_delete_fields(modified_do_dates)
        self.assertEqual(len(test_fields_to_delete), 1)
        for field in test_fields_to_delete:
            self.assertEqual(field.Field, 'dates')

    def test_delete_multiple_dates(self):
        test_fields_to_delete = parse_delete_fields(test_digital_object_dates)
        self.assertEqual(len(test_fields_to_delete), 1)
        for field in test_fields_to_delete:
            self.assertEqual(field.Field, 'dates')
            self.assertIsNot(field.Subrecord['label'], 'digitized')


class TestDeleteFieldInfo(unittest.TestCase):

    def test_delete_single_date(self):
        modified_do_dates = deepcopy(test_digital_object_dates)
        modified_do_dates['dates'].pop(1)
        deleted_dates_json = delete_field_info(modified_do_dates,
                                               'dates',
                                               modified_do_dates['dates'][0])
        self.assertIs(len(deleted_dates_json['dates']), 0)
        self.assertIsInstance(deleted_dates_json['dates'], list)

    def test_delete_multiple_dates(self):
        deleted_dates_json = delete_field_info(test_digital_object_dates,
                                               'dates',
                                               test_digital_object_dates['dates'][0])
        self.assertIs(len(deleted_dates_json['dates']), 1)
        self.assertIsInstance(deleted_dates_json['dates'][0], dict)
        self.assertIsInstance(deleted_dates_json['dates'], list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
