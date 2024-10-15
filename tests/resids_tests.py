# This script consists of unittests for update_resids.py
import json
import unittest

from python_scripts.update_resids import remove_nonalphanums
from python_scripts.update_znames import *
from secrets import *
# from test_data.resids_testdata import *


class TestClientLogin(unittest.TestCase):

    def test_default_connection(self):
        """Test using default connection info found in secrets.py"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        self.assertIsInstance(self.local_aspace, ASnakeClient)

    def test_error_connection(self):
        """Test using garbage input for ASnakeAuthError return"""
        self.local_aspace = client_login("https://www.cnn.com", "garbage", "garbage")
        self.assertEqual(self.local_aspace, ASnakeAuthError)


class TestRemoveAlphanums(unittest.TestCase):

    def test_no_change(self):
        """Tests that the returned string is not changed by remove_nonalphanums()"""
        no_changes = f'NMAI.AC.001.038'
        updated_value = remove_nonalphanums(no_changes)
        self.assertIsInstance(updated_value, str)
        self.assertEqual(no_changes, updated_value)

    def test_change_identifier(self):
        """Tests that the returned string is changed by remove_nonalphanums()"""
        change_value = f'''["NAA.1982-20:'''
        updated_value = remove_nonalphanums(change_value)
        self.assertIsInstance(updated_value, str)
        self.assertEqual(updated_value, f'NAA.1982.20')

    def test_non_ascii(self):
        """Tests that remove_nonalphanums() fails gracefully when encountering non-ASCII characters"""
        non_ascii_characters = {
            'no_alphanums': f'''!@#$%^&*()_|\\?'/,~` ''',
            'non_ascii': f'''é, à, ö, ñ, ü''',
            'non_latin': f'''漢, こんにちは, به متنی''',
            'symbols': f'''©, ®, €, £, µ, ¥''',
            'emojis': f'''😀, 🌍, 🎉, 👋'''}
        for incompatible_values in non_ascii_characters.values():
            no_value = remove_nonalphanums(incompatible_values)
            self.assertIsInstance(no_value, str)
            self.assertEqual(no_value, f'')


# class TestParseZnames(unittest.TestCase):
#
#     def test_good_user(self):
#         good_user = {'username': 'z-simong-expired-'}
#         updated_username = parse_znames(good_user)
#         self.assertEqual(updated_username.Error, False)
#         self.assertEqual(updated_username.Message, 'simong')
#
#     def test_username_not_match(self):
#         nonmatch_user = {'username': 'simong'}
#         update_username = parse_znames(nonmatch_user)
#         self.assertEqual(update_username.Error, True)
#         self.assertIn('!!ERROR!!: Username does not match:', update_username.Message)
#
#     def test_username_not_found(self):
#         no_username = {'namenotuser': 'simong'}
#         update_username = parse_znames(no_username)
#         self.assertEqual(update_username.Error, True)
#         self.assertIn('!!ERROR!!: No username found:', update_username.Message)


class TestUpdateResIds(unittest.TestCase):
    pass
#     def test_aspace_post_response(self):
#         self.local_aspace = client_login(as_api, as_un, as_pw)
#         updated_lock_version = self.local_aspace.get(f'/users/7').json()['lock_version']  # users/7 should be viewer
#         viewer_user['lock_version'] = updated_lock_version
#         test_response = update_usernames(self.local_aspace, viewer_user)
#         self.assertEqual(test_response['status'], 'Updated')
#         self.assertEqual(test_response['warnings'], [])
#
#     def test_bad_post(self):
#         self.local_aspace = client_login(as_api, as_un, as_pw)
#         viewer_user['username'] = 'laksdflilsadfkj'
#         viewer_user['uri'] = '/users/7155433575654654487'
#         test_response = update_usernames(self.local_aspace, viewer_user)
#         self.assertIn('error', test_response)
#         self.assertEqual(test_response['error'], 'User not found')


if __name__ == "__main__":
    unittest.main(verbosity=2)