# This script consists of unittests for update_coordinates.py
import unittest

from python_scripts.utilities import *
from python_scripts.one_time_scripts.update_coordinates import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
test_dbconnection = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                   int(os.getenv('db_port')))


class TestUpdateCoordinates(unittest.TestCase):

    def test_strip_zero_present(self):
        """Tests that a leading zero found within coordinate_1_indicator and coordinate_2_indicator are removed from
        a given dictionary"""
        test_location = {'coordinate_1_indicator': '01', 'coordinate_2_indicator': '01', }
        updated_test_location = strip_coordinate_leadzero(test_location)
        self.assertEqual(updated_test_location['coordinate_1_indicator'], '1')
        self.assertEqual(updated_test_location['coordinate_2_indicator'], '1')

    def test_strip_zero_missing(self):
        """Tests that indicators without a leading zero do not get changed"""
        test_location = {'coordinate_1_indicator': '100', 'coordinate_2_indicator': '100', }
        updated_test_location = strip_coordinate_leadzero(test_location)
        self.assertEqual(updated_test_location['coordinate_1_indicator'], '100')
        self.assertEqual(updated_test_location['coordinate_2_indicator'], '100')

    def test_strip_zero_no_coordinate(self):
        """Tests that the location data is not changed if there are no coordinates present"""
        test_location = {"lock_version": 1, "building": "Smithsonian", "title": "Smithsonian, Basement, Vault-110", "floor": "Basement", "room": "Vault-110", "uri": "/locations/99999", "owner_repo": {"ref": "/repositories/20"}}
        updated_test_location = strip_coordinate_leadzero(test_location)
        self.assertEqual(test_location, updated_test_location)

if __name__ == "__main__":
    unittest.main(verbosity=2)
