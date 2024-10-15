#!/usr/bin/env python

# This script consists of unittests for update_znames.py
import json
import unittest

from python_scripts.update_znames import *
from secrets import *
from test_data.znames_testdata import *


class TestClientLogin(unittest.TestCase):

    def test_default_connection(self):
        """Test using default connection info found in secrets.py"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        self.assertIsInstance(self.local_aspace, ASnakeClient)

    def test_error_connection(self):
        """Test using garbage input for ASnakeAuthError return"""
        self.local_aspace = client_login("https://www.cnn.com", "garbage", "garbage")
        self.assertEqual(self.local_aspace, ASnakeAuthError)


class TestGetUserData(unittest.TestCase):

    def test_users_data(self):
        """Tests that the returned users_data list is not empty"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        test_users = get_userdata(self.local_aspace)
        self.assertFalse(not test_users)
        self.assertIsInstance(test_users, list)

    def test_username_in_users_data(self):
        """Tests if users_data is in JSON and 'username' key is in returned users_data"""
        self.local_aspace = client_login(as_api, as_un, as_pw)
        test_users = get_userdata(self.local_aspace)
        for user in test_users:
            test_json = json.dumps(user)
            self.assertTrue(json.loads(test_json))  # This doesn't seem like the right way to do it...
            self.assertTrue("username" in user)


class TestParseZnames(unittest.TestCase):

    def test_good_user(self):
        good_user = {'username': 'z-simong-expired-'}
        updated_username = parse_znames(good_user)
        self.assertEqual(updated_username.Error, False)
        self.assertEqual(updated_username.Message, 'simong')

    def test_username_not_match(self):
        nonmatch_user = {'username': 'simong'}
        update_username = parse_znames(nonmatch_user)
        self.assertEqual(update_username.Error, True)
        self.assertIn('!!ERROR!!: Username does not match:', update_username.Message)

    def test_username_not_found(self):
        no_username = {'namenotuser': 'simong'}
        update_username = parse_znames(no_username)
        self.assertEqual(update_username.Error, True)
        self.assertIn('!!ERROR!!: No username found:', update_username.Message)


class TestUpdateUsernames(unittest.TestCase):

    def test_aspace_post_response(self):
        self.local_aspace = client_login(as_api, as_un, as_pw)
        updated_lock_version = self.local_aspace.get(f'/users/7').json()['lock_version']  # users/7 should be viewer
        viewer_user['lock_version'] = updated_lock_version
        test_response = update_usernames(self.local_aspace, viewer_user)
        self.assertEqual(test_response['status'], 'Updated')
        self.assertEqual(test_response['warnings'], [])

    def test_bad_post(self):
        self.local_aspace = client_login(as_api, as_un, as_pw)
        viewer_user['username'] = 'laksdflilsadfkj'
        viewer_user['uri'] = '/users/7155433575654654487'
        test_response = update_usernames(self.local_aspace, viewer_user)
        self.assertIn('error', test_response)
        self.assertEqual(test_response['error'], 'User not found')


if __name__ == "__main__":
    unittest.main(verbosity=2)
