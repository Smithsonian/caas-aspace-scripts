# This script consists of unittests for shared utilities.py
import contextlib
import io
import json
import os
import unittest

from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from python_scripts.one_time_scripts.delete_aaadigobjs import *
from python_scripts.utilities import *
from test_data.utilities_testdata import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
test_dbconnection = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                   int(os.getenv('db_port')))


class TestDeleteAAADigObjs(unittest.TestCase):
    good_aspace_connection = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))

    def test_good_archobj_refid(self):
        """Test to see if a valid refID outputs the SQL query as expected."""
        good_refid = "AAA.carninst_ref9955"
        test_query = update_query(good_refid)
        self.assertEqual(test_query, 'SELECT CONCAT("/repositories/30/digital_objects/", digobj.id) AS URI FROM `instance` AS inst JOIN instance_do_link_rlshp AS instrel ON instrel.instance_id = inst.id JOIN archival_object AS ao ON ao.id = inst.archival_object_id JOIN digital_object AS digobj ON digobj.id = instrel.digital_object_id WHERE ao.ref_id = "AAA.carninst_ref9955"')


    def test_good_archobj_refid(self):
        """Test to see if a valid refID outputs the SQL query as expected."""
        bad_refid = {"AAA.carninst_ref9955"}
        with self.assertRaises(TypeError):
            update_query(bad_refid)

if __name__ == "__main__":
    unittest.main(verbosity=2)