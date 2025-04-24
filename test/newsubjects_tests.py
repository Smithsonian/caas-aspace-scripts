# This script consists of unittests for new_subjects.py
import unittest

from python_scripts.repeatable.new_subjects import *
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
        test_subjects = read_csv(str(Path(f'./test_data/newsubjects_testdata.csv')))
        self.assertIsNotNone(test_subjects)
        for row in test_subjects:
            self.assertIsInstance(row, dict)

    def test_bad_csv(self):
        test_subjects = read_csv(str(Path(f'./test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_subjects, None)

class TestBuildSubject(unittest.TestCase):

    def test_build_subjects(self):
        """Tests that the subject is built as expected"""
        test_subjects = read_csv(str(Path(f'./test_data/newsubjects_testdata.csv')))
        for row in test_subjects:
            new_subj = build_subject(row)
            self.assertEqual(row['new_title'], new_subj['terms'][0]['term'])
            self.assertEqual('cultural_context', new_subj['terms'][0]['term_type'])
            self.assertEqual(row['new_scope_note'], new_subj['scope_note'])
            self.assertEqual('nmaict', new_subj['source'])
            self.assertEqual(row['new_EMu_ID'], new_subj['external_ids'][0]['external_id'])
            self.assertEqual('EMu_ID', new_subj['external_ids'][0]['source'])

class TestCreateSubjects(unittest.TestCase):

    def test_aspace_post_response(self):
        test_response = create_subject(local_aspace, test_new_subject_metadata)
        self.assertEqual(test_response['status'], 'Created')
        self.assertEqual(test_response['warnings'], [])

    def test_bad_post(self):
        test_response = create_subject(local_aspace, duplicate_new_subject)
        self.assertIn('error', test_response)
        self.assertEqual(test_response['error']['terms'], ['Subject must be unique'])

class TestAll(unittest.TestCase):

    # Mainly included as a (temporary?) shortcut to seeding data for update and merge unittests.
    def test_creation_from_csv(self):
        self.assertIsNone(main(f'./test_data/newsubjects_testdata.csv'))

if __name__ == "__main__":
    unittest.main(verbosity=2)
