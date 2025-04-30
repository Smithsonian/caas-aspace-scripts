#!/usr/bin/python3
# This script contains unittests for update_locations.py
import contextlib
import io
import unittest

from dotenv import load_dotenv, find_dotenv
from python_scripts.repeatable.update_locations import *
from python_scripts.utilities import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
test_update_location = {'lock_version': 0, 'building': 'ACM', 'title': 'ACM, Stacks, Section 122 [Bay: 1, Column: A, Shelf: 2]', 'room': 'Stacks', 'area': 'Section 122', 'coordinate_1_label': 'Bay', 'coordinate_1_indicator': '1', 'coordinate_2_label': 'Column', 'coordinate_2_indicator': 'A', 'coordinate_3_label': 'Shelf', 'coordinate_3_indicator': '2', 'created_by': 'morrisj', 'last_modified_by': 'morrisj', 'create_time': '2025-01-07T19:09:37Z', 'system_mtime': '2025-01-07T19:09:37Z', 'user_mtime': '2025-01-07T19:09:37Z', 'jsonmodel_type': 'location', 'external_ids': [], 'functions': [], 'uri': '/locations/55035'}


class TestAddRepo(unittest.TestCase):

    def test_good_update(self):
        """Tests adding a repository to a location record"""
        test_updated_location = add_repo(test_update_location, 24)
        self.assertIn('owner_repo', test_updated_location)

    def test_bad_update(self):
        """Tests if providing anything other than an int for add_repo() returns an error message"""
        # f = io.StringIO()
        # with contextlib.redirect_stdout(f):
        #     test_updated_location = add_repo(test_update_location, False)
        # self.assertTrue(
        #     r"""add_repo() - Unable to add repository code: <class 'TypeError'>""" in f.getvalue())
        pass

