# This script consists of unittests for merge_subjects.py
import unittest

from python_scripts.merge_subjects import *
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
        test_subjects = read_csv(str(Path(f'./test_data/mergesubjects_testdata.csv')))
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
        subject_id = test_merge_subject_destination['uri'].split('/subjects/')[1]
        test_response = get_subject(self.local_aspace, subject_id)
        self.assertIsInstance(test_response, dict)
        self.assertNotIn('error', test_response)

    def test_get_missing_subject(self):
        """Tests that a missing subject returns an error"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        test_response = get_subject(self.local_aspace, '600') # Some unusually high made up number
        self.assertIn('error', test_response)

class TestCheckSubject(unittest.TestCase):

    def test_check_subject(self):
        """Tests that a subject with matching id and title returns true"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        subject_id = test_merge_subject_destination['uri'].split('/subjects/')[1]
        check = check_subject(self.local_aspace, subject_id, 'title 2')
        self.assertTrue(check)
    
    def test_check_subject(self):
        """Tests that a subject with mis-matched id and title returns false"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        subject_id = test_merge_subject_destination['uri'].split('/subjects/')[1]
        check = check_subject(self.local_aspace, subject_id, 'Wrong title')
        self.assertFalse(check)

class TestMergeSubjects(unittest.TestCase):

    def test_aspace_post_response(self):
        self.local_aspace = client_login(as_api, as_un, as_pw)
        test_response = merge_subject(self.local_aspace, test_merge_subject_destination['uri'], test_merge_subject_candidate['uri'])
        self.assertEqual(test_response['status'], 'Merged')
        self.assertEqual(test_response['target_uri'], test_merge_subject_destination['uri'])
        self.assertEqual(test_response['deleted_uris'][0], test_merge_subject_candidate['uri'])

    def test_bad_post(self):
        self.local_aspace = client_login(as_api, as_un, as_pw)
        test_response = merge_subject(self.local_aspace, test_merge_subject_destination['uri'], '/subjects/600') # Some unusually high made up number
        print(test_response)
        self.assertIn('error', test_response)
        self.assertEqual(test_response['error'], 'Subject not found')

if __name__ == "__main__":
    unittest.main(verbosity=2)
