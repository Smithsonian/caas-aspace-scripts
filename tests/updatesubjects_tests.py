# This script consists of unittests for new_subjects.py
import json
import unittest

from python_scripts.update_subjects import *
from secrets import *
from test_data.subjects_testdata import *

class TestClientLogin(unittest.TestCase):

    def test_default_connection(self):
        """Test using default connection info found in secrets.py"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        self.assertIsInstance(self.local_aspace, ASnakeClient)

    def test_error_connection(self):
        """Test using garbage input for ASnakeAuthError return"""
        self.local_aspace = client_login("https://www.cnn.com", "garbage", "garbage")
        self.assertEqual(self.local_aspace, ASnakeAuthError)

class TestReadCSV(unittest.TestCase):

    def test_good_csv(self):
        test_subjects = read_csv(str(Path(f'./test_data/updatesubjects_testdata.csv')))
        self.assertIsNotNone(test_subjects)
        for row in test_subjects:
            self.assertIsInstance(row, dict)

    def test_bad_csv(self):
        test_subjects = read_csv(str(Path(f'./test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_subjects, None)

class TestGetSubject(unittest.TestCase):

    def test_get_subject(self):
        """Tests that the existing subject can be retrieved"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        subject_id = test_update_subject_metadata['uri'].split('/subjects/')[1]
        test_response = get_subject(self.local_aspace, subject_id)
        self.assertIsInstance(test_response, dict)
        self.assertNotIn('error', test_response)

    def test_get_missing_subject(self):
        """Tests that a missing subject returns an error"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        test_response = get_subject(self.local_aspace, '600') # Some unusually high made up number
        self.assertIn('error', test_response)

class TestBuildSubject(unittest.TestCase):

    def test_build_subjects(self):
        """Tests that the subject is built as expected"""
        test_subjects = read_csv(str(Path(f'./test_data/updatesubjects_testdata.csv')))
        for row in test_subjects:
            updated_subj = build_subject(test_update_subject_metadata, row)
            self.assertEqual(row['new_title'], updated_subj['terms'][0]['term'])
            self.assertEqual('cultural_context', updated_subj['terms'][0]['term_type'])
            self.assertEqual(row['new_scope_note'], updated_subj['scope_note'])
            self.assertEqual('nmaict', updated_subj['source'])
            self.assertEqual(row['new_EMu_ID'], updated_subj['external_ids'][0]['external_id'])
            self.assertEqual('EMu_ID', updated_subj['external_ids'][0]['source'])

class TestUpdateSubjects(unittest.TestCase):

    def test_aspace_post_response(self):
        self.local_aspace = client_login(as_api, as_un, as_pw)
        subject_id = test_update_subject_metadata['uri'].split('/subjects/')[1]
        test_response = update_subject(self.local_aspace, subject_id, test_update_subject_metadata)
        self.assertEqual(test_response['status'], 'Updated')
        self.assertEqual(test_response['warnings'], [])

    def test_bad_post(self):
        self.local_aspace = client_login(as_api, as_un, as_pw)
        test_response = update_subject(self.local_aspace, '600', test_update_subject_metadata) # Some unusually high made up number
        self.assertIn('error', test_response)
        self.assertEqual(test_response['error'], 'Subject not found')

if __name__ == "__main__":
    unittest.main(verbosity=2)
