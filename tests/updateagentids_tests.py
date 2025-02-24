#!/usr/bin/python3
# This script contains unittests for update_agentids.py
import contextlib
import io
import pandas
import unittest

from python_scripts.one_time_scripts.update_agentids import *
from test_data.updateagentids_testdata import *

class TestAddRecordID(unittest.TestCase):

    def test_good_record(self):
        """Tests to see if the record ID, source, jsonmodel_type, and primary are set correctly for add_recordID()"""
        test_updated_object = add_recordID(test_record_id, test_record_source, test_object_json)
        self.assertIsNotNone(test_updated_object["agent_record_identifiers"])
        self.assertEqual(test_updated_object["agent_record_identifiers"][-1]["record_identifier"], "36102023")
        self.assertEqual(test_updated_object["agent_record_identifiers"][-1]["source"], "snac")
        self.assertEqual(test_updated_object["agent_record_identifiers"][-1]["jsonmodel_type"],
                         "agent_record_identifier")
        self.assertFalse(test_updated_object["agent_record_identifiers"][-1]["primary_identifier"])

    def test_bad_record_id(self):
        """Tests that a TypeError is raised if supplied with a record ID that is not an integer"""
        with self.assertRaises(TypeError):
            add_recordID(13213215, test_record_source, test_object_json)

    def test_bad_record_source(self):
        """Tests that a TypeError is raised if supplied with an integer for the record source"""
        with self.assertRaises(TypeError):
            add_recordID(test_record_id, 12043201, test_object_json)


class TestCheckIDs(unittest.TestCase):

    def test_id_mismatch(self):
        check_ids_status = check_ids(test_record_source, test_record_id, test_object_json)
        self.assertFalse(check_ids_status)

    def test_id_match(self):
        test_good_identifier = "10499608"
        check_ids_status = check_ids(test_record_source, test_good_identifier, test_object_json)
        self.assertTrue(check_ids_status)

    def test_no_source(self):
        test_no_source = "lcnaf"
        check_ids_status = check_ids(test_no_source, test_record_id, test_object_json)
        self.assertIsNone(check_ids_status)

if __name__ == "__main__":
    unittest.main(verbosity=2)
