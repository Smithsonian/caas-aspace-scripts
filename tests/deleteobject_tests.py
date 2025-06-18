# This script consists of unittests for delete_object.py
import contextlib
import io
import random
import unittest

from python_scripts.repeatable.delete_objects import *
from python_scripts.utilities import *
from test_data.utilities_testdata import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))

class TestArchivesSpaceClass(unittest.TestCase):
    good_aspace_connection = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))

    def test_global_uri(self):
        """Tests a global URI for an object returns said objects' JSON data"""
        test_location = self.good_aspace_connection.aspace_client.post("/locations", json=test_location_delete).json()
        test_global = retrieve_object_json({'uri': test_location['uri']}, self.good_aspace_connection)
        self.assertIsNotNone(test_global)
        self.assertEqual(test_global['title'], 'NMAH-SHF [Test Shelf: 602668]')
        test_delete = self.good_aspace_connection.delete_object(test_location['uri'])
        print(test_delete)

    def test_local_uri(self):
        """Tests that a local URI (one beginning with 'repositories/##/' is retrieved"""
        uri_parts = test_digital_object_dates['uri'].split('/')
        test_digobj = self.good_aspace_connection.get_object(uri_parts[-2], uri_parts[-1], f'{uri_parts[1]}/{uri_parts[2]}')
        if test_digobj:
            get_test_digobj = retrieve_object_json({'uri': test_digobj['uri']}, self.good_aspace_connection)
            self.assertIsNotNone(get_test_digobj)
            self.assertEqual(get_test_digobj['digital_object_id'], 'NMAI.AC.066.ref20')
        else:
            test_digital_object_dates['digital_object_id'] = f'NMAI.AC.066.ref{random.randint(1, 100)}'
            test_digobj_new = self.good_aspace_connection.aspace_client.post('/repositories/12/digital_objects',
                                                                             json=test_digital_object_dates).json()
            get_test_digobj_new = retrieve_object_json({'uri': test_digobj_new['uri']}, self.good_aspace_connection)
            self.assertIsNotNone(get_test_digobj_new)
            self.assertTrue((get_test_digobj_new['digital_object_id']).startswith('NMAI.AC.066.ref'))

    def test_bad_uri(self):
        """Tests that a bad URI throws an error"""
        test_bad_uri = {'uri': '110203/locations/%^^!!!'}
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            test_response = retrieve_object_json(test_bad_uri, self.good_aspace_connection)

        self.assertTrue(
            r"""get_object() - Unable to retrieve object with provided URI: /locations/%^^!!!: {'error': {'id': ["Wanted type Integer but got '%^^!!!'"]}}""" in f.getvalue())
        self.assertIsNone(test_response)

    def test_bad_separator(self):
        test_bad_uri = {'uri': '110203,locations,%^^!!!'}
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            test_response = retrieve_object_json(test_bad_uri, self.good_aspace_connection)
            print(test_response)
        self.assertTrue(
            r"""retrieve_object_json() - Failed to split URI: list index out of range""" in f.getvalue())
        self.assertIsNone(test_response)


if __name__ == "__main__":
    unittest.main(verbosity=2)
