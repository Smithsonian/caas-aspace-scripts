# This script consists of unittests for merge_subjects.py
import unittest

from python_scripts.repeatable.update_fileuri import *
from test_data.fileuri_testdata import *

# Hardcode to dev env
env_file = find_dotenv(f'.env.dev')
load_dotenv(env_file)
local_aspace = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))

class TestGetDigitalObject(unittest.TestCase):

    def test_get_digital_object(self):
        """Tests that the existing digital object can be retrieved"""
        repo_id = test_update_file_uri_metadata['repository']['ref'].split('/repositories/')[1]
        digital_object_id = test_update_file_uri_metadata['uri'].rsplit('/',1)[1]
        test_response = get_digital_object(local_aspace, repo_id, digital_object_id)
        self.assertIsInstance(test_response, dict)
        self.assertNotIn('error', test_response)

    def test_get_missing_digital_object(self):
        """Tests that a missing digital object returns an error"""
        repo_id = test_update_file_uri_metadata['repository']['ref'].split('/repositories/')[1]
        test_response = get_digital_object(local_aspace, repo_id, '600') # Some unusually high made up number
        self.assertIsNone(test_response)

class TestBuildDigitalObject(unittest.TestCase):

    def test_build_digital_object(self):
        """Tests that the digital object is built as expected"""
        test_dos = read_csv(str(Path(f'./test_data/updatefileuri_testdata.csv')))
        for row in test_dos:
            updated_do = build_digital_object(test_update_file_uri_metadata, row['updated_file_uri'])
            self.assertEqual(row['updated_file_uri'], updated_do['file_versions'][0]['file_uri'])

class TestDigitalObjects(unittest.TestCase):

    def test_aspace_post_response(self):
        repo_id = test_update_file_uri_metadata['repository']['ref'].split('/repositories/')[1]
        digital_object_id = test_update_file_uri_metadata['uri'].rsplit('/',1)[1]
        test_response = update_digital_object(local_aspace, repo_id, digital_object_id, test_update_file_uri_metadata)
        self.assertEqual(test_response['status'], 'Updated')
        self.assertEqual(test_response['warnings'], [])

    def test_bad_post(self):
        repo_id = test_update_file_uri_metadata['repository']['ref'].split('/repositories/')[1]
        test_response = update_digital_object(local_aspace, repo_id, '600', test_update_file_uri_metadata) # Some unusually high made up number
        self.assertIn('error', test_response)
        self.assertEqual(test_response['error'], 'DigitalObject not found')

if __name__ == "__main__":
    unittest.main(verbosity=2)
