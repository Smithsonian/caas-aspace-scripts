# This script consists of unittests for update_locationbuilding.py
import contextlib
import io
import unittest

from python_scripts.utilities import *
from python_scripts.one_time_scripts.update_locationbuildingfloor import *
from test_data.location_testdata import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
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
        test_location_uris = ["/locations/48008", "/locations/48009"] # TODO: change these?
        updated_test_location = update_building_name(test_location_uris, test_name, local_aspace)
        self.assertIsInstance(updated_test_location, list)
        self.assertEqual(len(updated_test_location), 2)

class TestMoveRoomToFloor(unittest.TestCase):

    def test_good_room(self):
        """Tests that good data found in the Room field overwrites the data in the Floor field and deleted from
        the Room field"""
        room_to_floor_updated = move_room_to_floor(test_location)
        self.assertEqual(room_to_floor_updated['floor'], test_location['room'])
        self.assertEqual(room_to_floor_updated['room'], '')

    def test_null_room(self):
        """Tests that if there is no value in the room field, the floor field remains the same"""
        test_location['room'] = None
        no_room = move_room_to_floor(test_location)
        self.assertIsNone(no_room)

    def test_missing_keys(self):
        """Tests that if either the Floor or Room keys are absent in the given location, nothing is returned"""
        copied_location = deepcopy(test_location)
        copied_location.pop('floor')
        copied_location.pop('room')
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            no_room_floor = move_room_to_floor(copied_location)
        self.assertTrue(
            r"""move_room_to_floor() - Room field not found in""" in f.getvalue())
        self.assertIsNone(no_room_floor)




if __name__ == "__main__":
    unittest.main(verbosity=2)
