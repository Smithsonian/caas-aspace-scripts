# This script consists of unittests for update_znames.py
import copy
import json
import unittest

from python_scripts.remove_missingtitles import *
from secrets import *
from test_data.missingtitles_testdata import *


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
        test_missinguris = read_csv(str(Path(f'../test_data/MissingTitles_BeGone.csv')))
        self.assertIsNotNone(test_missinguris)
        self.assertIsInstance(test_missinguris[1], str)

    def test_bad_csv(self):
        test_missinguris = read_csv(str(Path(f'../test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_missinguris, None)


class TestGetObjects(unittest.TestCase):

    def test_missing_title(self):
        """Tests that the returned users_data list is not empty"""
        test_newobj = get_objects(test_object_metadata, test="UNITTEST")
        for note in test_newobj.Message['notes']:
            if 'subnotes' in note:
                for subnote in note['subnotes']:
                    if 'title' in subnote:
                        self.fail(f'title found in {test_newobj.Message}')

    def test_no_title(self):
        """Tests if users_data is in JSON and 'username' key is in returned users_data"""
        test_newobj = get_objects(test_object_metadata, test="UNITTEST")
        test_updated_object = get_objects(test_newobj.Message, test="UNITTEST")
        self.assertEqual(test_updated_object.Status, "PASS")
        self.assertIn("No title in", test_updated_object.Message)

    def test_no_note_content(self):
        test_newobj = get_objects(test_object_metadata, test="UNITTEST")
        test_newobj.Message['notes'] = []
        test_updated_object = get_objects(test_newobj.Message, test="UNITTEST")
        self.assertEqual(test_updated_object.Status, "PASS")
        self.assertIn("No notes with content in", test_updated_object.Message)

    def test_no_notes(self):
        test_newobj = get_objects(test_object_metadata, test="UNITTEST")
        test_newobj.Message.pop('notes', None)
        test_updated_object = get_objects(test_newobj.Message, test="UNITTEST")
        self.assertEqual(test_updated_object.Status, "PASS")
        self.assertIn("No notes in", test_updated_object.Message)


class TestDeleteMissingTitle(unittest.TestCase):

    def test_missing_title_notes(self):
        test_delete = delete_missingtitle(test_notes)
        for note in test_delete:
            if 'subnotes' in note:
                for subnote in note['subnotes']:
                    if 'title' in subnote:
                        self.fail(f'title found in {test_delete}')

    def test_no_missing_title_note(self):
        no_title_notes = copy.deepcopy(test_notes)
        for note in no_title_notes:
            if 'subnotes' in note:
                for subnote in note['subnotes']:
                    if 'title' in subnote:
                        subnote.pop('title', None)
        test_delete = delete_missingtitle(no_title_notes)
        self.assertTrue(len(test_delete) == 0)


class TestUpdateObject(unittest.TestCase):

    def test_aspace_post_response(self):
        self.local_aspace = client_login(as_api, as_un, as_pw)
        updated_lock_version = self.local_aspace.get(f'{test_object_metadata["uri"]}').json()['lock_version']
        test_object_metadata['lock_version'] = updated_lock_version
        test_response = update_object(self.local_aspace, test_object_metadata['uri'], test_object_metadata)
        self.assertEqual(test_response['status'], 'Updated')
        self.assertEqual(test_response['warnings'], [])

    def test_bad_post(self):
        self.local_aspace = client_login(as_api, as_un, as_pw)
        updated_lock_version = self.local_aspace.get(f'{test_object_metadata["uri"]}').json()['lock_version']
        test_object_metadata['lock_version'] = updated_lock_version
        test_object_metadata['uri'] = 'lkjsadlkjiidifakdsj'  # Bad URI
        test_response = update_object(self.local_aspace, test_object_metadata['uri'], test_object_metadata)
        self.assertIn('error', test_response)


if __name__ == "__main__":
    unittest.main(verbosity=2)
