# This script consists of unittests for new_subjects.py
import unittest

from python_scripts.repeatable.update_subjects import *
from test_data.subjects_testdata import *

env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
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
        test_subjects = read_csv(str(Path('./test_data/updatesubjects_testdata.csv')))
        self.assertIsNotNone(test_subjects)
        for row in test_subjects:
            self.assertIsInstance(row, dict)

    def test_bad_csv(self):
        test_subjects = read_csv(str(Path('./test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_subjects, None)

class TestGetSubject(unittest.TestCase):

    def test_get_subject(self):
        """Tests that the existing subject can be retrieved"""
        subject_id = test_update_subject_metadata['uri'].split('/subjects/')[1]
        test_response = get_subject(local_aspace, subject_id)
        self.assertIsInstance(test_response, dict)
        self.assertNotIn('error', test_response)

    def test_get_missing_subject(self):
        """Tests that a missing subject returns None"""
        test_response = get_subject(local_aspace, '600') # Some unusually high made up number
        self.assertIsNone(test_response)

class TestBuildSubject(unittest.TestCase):

    def test_build_subjects(self):
        """Tests that the subject is built as expected"""
        test_subjects = read_csv(str(Path('./test_data/updatesubjects_testdata.csv')))
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
        subject_id = test_update_subject_metadata['uri'].split('/subjects/')[1]
        test_response = update_subject(local_aspace, subject_id, test_update_subject_metadata)
        self.assertEqual(test_response['status'], 'Updated')
        self.assertEqual(test_response['warnings'], [])

    def test_bad_post(self):
        test_response = update_subject(local_aspace, '600', test_update_subject_metadata) # Some unusually high made up number
        self.assertIn('error', test_response)
        self.assertEqual(test_response['error'], 'Subject not found')

if __name__ == "__main__":
    unittest.main(verbosity=2)
