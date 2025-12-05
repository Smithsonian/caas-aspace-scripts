# This script consists of unittests for update_locationbuilding.py
import unittest

from python_scripts.utilities import *
from python_scripts.one_time_scripts.update_locationbuilding import *
from test_data.location_testdata import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
test_dbconnection = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                   int(os.getenv('db_port')))


class TestUpdateLocationBuilding(unittest.TestCase):

    def test_location_ids(self):
        """Tests that an existing building location returns a list of matching location IDs"""
        test_building = "NMAH-SHF, Building 19"
        test_results = location_ids(test_building, test_dbconnection)
        self.assertIsInstance(test_results, list)
        self.assertIsInstance(test_results[0], int)
        self.assertTrue(len(test_results) > 0)

class TestUpdateBuildingName(unittest.TestCase):

    def test_valid_name(self):
        """Tests that a location JSON object is updated with a new building name in the building field"""
        test_name = "Gutiokipanja"
        updated_test_location = update_building_name(test_location, test_name)
        self.assertIsInstance(updated_test_location, dict)
        self.assertEqual(updated_test_location['building'], test_name)

    def test_no_building_key(self):
        """Tests that a location JSON object is not updated and None is returned if the building key is not found"""
        test_name = "Gutiokipanja"
        updated_test_location = update_building_name(test_nobuilding_location, test_name)
        self.assertIsNone(updated_test_location)



if __name__ == "__main__":
    unittest.main(verbosity=2)
