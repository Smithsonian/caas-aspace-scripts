#!/usr/bin/python3
# This script contains unittests for suppress_objects.py
import contextlib
import io
import unittest

from python_scripts.repeatable.suppress_objects import *
from test_data.suppressobjects_testdata import *


class TestUpdatePublishStatus(unittest.TestCase):

    def test_good_update(self):
        """Tests that a provided resource has it's publish and finding_aid_status fields updated"""
        updated_resource = update_publish_status(published_resource, "resources")
        self.assertEqual(updated_resource['publish'], False)
        self.assertEqual(updated_resource['finding_aid_status'], "staff_only")

    def test_bad_type(self):
        """Tests inputting a bad object type that isn't in the list of resources, archival_objects, or
        digital_objects"""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            update_publish_status(published_resource, "laksdjflkj")

        self.assertTrue(
            r"""update_publish_status() - provided object type is not in ['resources', 'archival_objects', 'digital_objects']: <class 'ValueError'>""" in f.getvalue())

