# This script consists of unittests for shared report_sovatreeview.py
import unittest

from python_scripts.one_time_scripts.delete_aaadigobjs import *
from python_scripts.one_time_scripts.report_sovatreeview import has_treeview
from python_scripts.utilities import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
test_dbconnection = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                   int(os.getenv('db_port')))


class TestReportSovaTreeView(unittest.TestCase):
    good_aspace_connection = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))

    def test_good_treeview(self):
        """Tests that a good treeview URL returns True"""
        good_treeview = "https://sova.si.edu/fancytree/aaa.bartmace"
        treeview_status = has_treeview(good_treeview)
        self.assertTrue(treeview_status)

    def test_no_treeview(self):
        """Tests that a treeview URL that has no treeview returns False"""
        no_treeview = "https://sova.si.edu/fancytree/naa.3033.12"
        treeview_status = has_treeview(no_treeview)
        self.assertFalse(treeview_status)


if __name__ == "__main__":
    unittest.main(verbosity=2)