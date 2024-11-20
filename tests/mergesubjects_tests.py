# This script consists of unittests for merge_subjects.py
import unittest

from python_scripts.merge_subjects import *
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
        subject_id = test_merge_subject_destination['uri'].split('/subjects/')[1]
        test_response = get_subject(local_aspace, subject_id)
        self.assertIsInstance(test_response, dict)
        self.assertNotIn('error', test_response)

    def test_get_missing_subject(self):
        """Tests that a missing subject returns an error"""
        test_response = get_subject(local_aspace, '600') # Some unusually high made up number
        self.assertIsInstance(test_response, dict)
        self.assertIn('error', test_response)

class TestCheckSubject(unittest.TestCase):

    def test_good_subject(self):
        """Tests that a subject with matching id and title returns True"""
        subject_id = test_merge_subject_destination['uri'].split('/subjects/')[1]
        check = check_subject(local_aspace, subject_id, 'title 2')
        self.assertTrue(check)
    
    def test_bad_subject(self):
        """Tests that a subject with mis-matched id and title returns false"""
        subject_id = test_merge_subject_destination['uri'].split('/subjects/')[1]
        check = check_subject(local_aspace, subject_id, 'Wrong title')
        self.assertFalse(check)

    def test_missing_subject(self):
        """Tests that a subject that does not exist returns None"""
        check = check_subject(local_aspace, '600', 'Wrong title') # Some unusually high made up number
        self.assertIsNone(check)

class TestMergeSubjects(unittest.TestCase):

    def test_aspace_post_response(self):
        test_response = merge_subject(local_aspace, test_merge_subject_destination['uri'], test_merge_subject_candidate['uri'])
        self.assertEqual(test_response['status'], 'Merged')
        self.assertEqual(test_response['target_uri'], test_merge_subject_destination['uri'])
        self.assertEqual(test_response['deleted_uris'][0], test_merge_subject_candidate['uri'])

    def test_bad_post(self):
        test_response = merge_subject(local_aspace, test_merge_subject_destination['uri'], '/subjects/600') # Some unusually high made up number
        print(test_response)
        self.assertIn('error', test_response)
        self.assertEqual(test_response['error'], 'Subject not found')

if __name__ == "__main__":
    unittest.main(verbosity=2)
