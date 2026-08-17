# This script consists of unittests for remove_datetimestamps.py
import contextlib
import io
import unittest

from python_scripts.repeatable.remove_datetimestamps import *
from python_scripts.utilities import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
test_dbconnection = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                   int(os.getenv('db_port')))


class TestUpdateDate(unittest.TestCase):

    def test_good_date(self):
        """Test that a date is stripped of whitespace and the timestamp"""
        example_date = ' 2023-10-20T15:35:39Z '
        new_date = update_date(example_date)
        self.assertEqual(new_date, '2023-10-20')

    def test_bad_date(self):
        """Test an incorrectly formatted date produces a warning message"""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            bad_example = ' 1946-06-06aaaaaaa '
            update_date(bad_example)
            print(f.getvalue())
            self.assertTrue('The following date is longer than 10 characters: 1946-06-06aaaaaaa' in f.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
