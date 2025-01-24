# This script consists of unittests for shared utilities.py
import contextlib
import io
import json
import os
import unittest

from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from python_scripts.utilities import *
from test_data.utilities_testdata import *

# Hardcode to dev env
env_file = find_dotenv(f'.env.dev')
load_dotenv(env_file)
local_aspace = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
test_dbconnection = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                   int(os.getenv('db_port')))


class TestArchivesSpaceClass(unittest.TestCase):
    good_aspace_connection = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))

    def test_asnake_connection(self):
        """Tests a good connection to ArchivesSnake creates an ASnakeClient class for the aspace_client instance
        variable"""
        self.assertIsInstance(self.good_aspace_connection.aspace_client, ASnakeClient)

    def test_bad_connection(self):
        """Tests that a bad connection to the ArchivesSpace API raises an ASnakeAuthError"""
        with self.assertRaises(ASnakeAuthError):
            ASpaceAPI(os.getenv('as_api'), "bad_user", "bad_password")

    def test_get_repoinfo(self):
        """Tests getting repository info for all repositories in an ArchivesSpace instance in list form"""
        repos_info = self.good_aspace_connection.get_repo_info()
        self.assertIsInstance(repos_info, list)
        self.assertIn('uri', repos_info[1].keys())

    def test_get_digobjs_all(self):
        """Tests getting all IDs of digital objects returns a list of all digital object IDs from the API"""
        self.good_aspace_connection.get_repo_info()
        test_digitalobjects = self.good_aspace_connection.get_objects(self.good_aspace_connection.repo_info[1]['uri'],
                                                                 test_record_type,
                                                                 ('all_ids', True))
        self.assertIsInstance(test_digitalobjects, list)
        self.assertIsNot(len(test_digitalobjects), 0)
        self.assertIsInstance(test_digitalobjects[0], int)

    def test_get_digobjs_page(self):
        """Tests getting page 1 of all digital objects returns the first page of digital objects from the API"""
        self.good_aspace_connection.get_repo_info()
        test_digitalobjects = self.good_aspace_connection.get_objects(self.good_aspace_connection.repo_info[1]['uri'],
                                                                 test_record_type,
                                                                 ('page', 1))
        self.assertIsInstance(test_digitalobjects, dict)
        self.assertIsNot(len(test_digitalobjects), 0)
        self.assertIs(test_digitalobjects['first_page'], 1)

    def test_get_digobjs_set(self):
        """Tests getting an ID Set of digital objects returns the list of digital objects from the API"""
        self.good_aspace_connection.get_repo_info()
        id_set_values = [20,1204715,314276]
        test_digitalobjects = self.good_aspace_connection.get_objects(self.good_aspace_connection.repo_info[1]['uri'],
                                                                 test_record_type,
                                                                 ('id_set', id_set_values))
        self.assertIsInstance(test_digitalobjects, list)
        self.assertIsNot(len(test_digitalobjects), 0)
        for digital_object in test_digitalobjects:
            self.assertIs(type(digital_object[0]), dict)

    def test_get_digobj(self):
        """Tests getting a digital object via the API returns the digital object in a dict"""
        test_do_json = self.good_aspace_connection.get_object(test_record_type,
                                                         test_object_id,
                                                         test_object_repo_uri)
        self.assertIsInstance(test_do_json, dict)
        self.assertEqual(test_do_json['digital_object_id'], test_object_user_identifier)

    def test_bad_digobj(self):
        """Tests getting a digital object that doesn't exist prints/logs an error"""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            self.good_aspace_connection.get_object(test_record_type,
                                              10000000000000000,
                                              test_object_repo_uri)

        self.assertTrue(
            r"""get_object() - Unable to retrieve object with provided URI: {'error': 'DigitalObject not found'}""" in f.getvalue())

    def test_aspace_post_response(self):
        """Tests that a post with an existing URI returns Status: Updated and no warnings"""
        original_object_json = self.good_aspace_connection.get_object(test_record_type,
                                                                 test_object_id,
                                                                 test_object_repo_uri)
        test_response = self.good_aspace_connection.update_object(original_object_json['uri'],
                                                             original_object_json)
        self.assertEqual(test_response['status'], 'Updated')
        self.assertEqual(test_response['warnings'], [])

    def test_bad_post(self):
        """Tests that a post containing a bad URI returns None with the response"""
        original_object_json = self.good_aspace_connection.get_object(test_record_type,
                                                                 test_object_id,
                                                                 test_object_repo_uri)
        original_object_json['uri'] = 'laksjdlfieklkjfa'
        test_response = self.good_aspace_connection.update_object(original_object_json['uri'],
                                                             original_object_json)
        self.assertIsNone(test_response)


class TestASpaceDatabaseClass(unittest.TestCase):

    def test_good_connection(self):
        """Tests connection with good credentials as founds within the secrets.py file"""
        self.assertIsNotNone(test_dbconnection.connection)
        self.assertIsNotNone(test_dbconnection.cursor)

    def test_bad_connection(self):
        """Tests that an error is raised with making a connection with a bad username and password using the database
        found in the secrets.py file"""
        with self.assertRaises(mysql.Error):
            ASpaceDatabase('bad_un', 'bad_pw', 'bad_host', os.getenv('db_name'),
                               int(os.getenv('db_port')))

    def test_good_query(self):
        """Tests that the query_database() function returns a list of users from an ASpace database"""
        test_query = ('SELECT name, username FROM user')
        test_results = test_dbconnection.query_database(test_query)
        self.assertIsNotNone(test_results)
        self.assertIsInstance(test_results, list)

    def test_bad_query(self):
        """Tests that a badly formatted SQL query will raise a mysql.Error"""
        test_bad_query = ('SELECT nothing, username FROM user')
        with self.assertRaises(mysql.Error):
            test_dbconnection.query_database(test_bad_query)


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
        """Tests reading an existing CSV file and returns data"""
        test_subjects = read_csv(str(Path(f'./test_data/mergesubjects_testdata.csv')))
        self.assertIsNotNone(test_subjects)
        for row in test_subjects:
            self.assertIsInstance(row, dict)

    def test_bad_csv(self):
        """Tests reading a non-existant CSV returns a FileNotFound error and that test_subjects is None"""
        test_subjects = read_csv(str(Path(f'./test_data/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_subjects, None)


class TestCheckUrl(unittest.TestCase):

    def test_check_url(self):
        """Tests that an existing url returns True"""
        test_response = check_url('https://example.com')
        self.assertIsInstance(test_response, bool)
        self.assertTrue(test_response)

    def test_check_missing_url(self):
        """Tests that a broken url returns None"""
        test_response = check_url('https://www.si.edu/nothinghere')  # A bad url
        self.assertIsNone(test_response)

class TestWriteToFile(unittest.TestCase):

    def test_new_data(self):
        """Tests creating a new jsonlines file for original metadata saving if needed in case of data remediation"""
        test_filepath = str(Path('../test_data', 'test_create_original_metadata_file.jsonl'))
        if os.path.isfile(test_filepath):
            os.remove(test_filepath)
        write_to_file(test_filepath, test_digital_object_dates)
        self.assertTrue(os.path.isfile(test_filepath))
        with open(test_filepath, 'r') as test_reader:
            for row_data in test_reader:
                test_data = json.loads(row_data)
                self.assertEqual(test_data['digital_object_id'], test_digital_object_dates['digital_object_id'])
        os.remove(test_filepath)

    def test_append_data(self):
        """Tests appending to an existing jsonlines file"""
        test_filepath = str(Path('../test_data', 'test_update_locations_original_data.jsonl'))
        if os.path.isfile(test_filepath):
            os.remove(test_filepath)
        write_to_file(test_filepath, test_digital_object_dates)
        self.assertTrue(os.path.isfile(test_filepath))
        write_to_file(test_filepath, test_digital_object_dates_deleted)
        with open(test_filepath, 'r') as test_reader:
            counter = 0
            for row_data in test_reader:
                counter += 1
                test_data = json.loads(row_data)
                if counter == 1:
                    self.assertEqual(test_data['digital_object_id'],
                                     test_digital_object_dates['digital_object_id'])
                if counter == 2:
                    self.assertEqual(test_data['digital_object_id'],
                                     test_digital_object_dates_deleted['digital_object_id'])
            self.assertEqual(counter, 2)
        os.remove(test_filepath)

    def test_bad_file(self):
        """Tests trying to make a jsonlines file with a bad filename, which should log and print an error"""
        test_filepath = str(Path('../test_data', 'test_bad_filepath$&@.jID(#*&^%'))
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            write_to_file(test_filepath, test_digital_object_dates)
        self.assertTrue(r"""write_to_file() - Unable to open or access jsonl file: [Errno 22] Invalid argument: '..\\test_data\\test_bad_filepath$&@.jID(#*&^%'""" in f.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
