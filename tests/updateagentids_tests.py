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
        self.assertEqual(test_updated_object["agent_record_identifiers"][1]["record_identifier"], "36102023")
        self.assertEqual(test_updated_object["agent_record_identifiers"][1]["source"], "lcnaf")
        self.assertEqual(test_updated_object["agent_record_identifiers"][1]["jsonmodel_type"],
                         "agent_record_identifier")
        self.assertFalse(test_updated_object["agent_record_identifiers"][1]["primary_identifier"])

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
        test_nonmatch = "122528621"
        check_ids_status = check_ids(test_record_source, test_nonmatch, test_object_json)
        self.assertFalse(check_ids_status.Status)
        self.assertEqual(check_ids_status.Record, test_object_json["agent_record_identifiers"][1])

    def test_id_match(self):
        check_ids_status = check_ids(test_record_source, test_record_id, test_object_json)
        self.assertTrue(check_ids_status.Status)
        self.assertEqual(check_ids_status.Record, test_object_json["agent_record_identifiers"][1])

    def test_no_source(self):
        test_no_source = "bibframe"
        check_ids_status = check_ids(test_no_source, test_record_id, test_object_json)
        self.assertIsNone(check_ids_status.Status)
        self.assertIsNone(check_ids_status.Record)


class TestSortRecordIdentifiers(unittest.TestCase):

    def test_good_sources(self):
        sort_order = ["wikidata", "snac", "lcnaf", "ulan", "viaf"]
        test_sorted_sources = sort_identifiers(test_object_json)
        record_index = 0
        for record in test_sorted_sources["agent_record_identifiers"]:
            if record_index == 0:
                self.assertEqual(record['source'], sort_order[0])
            elif record_index == 1:
                self.assertEqual(record['source'], sort_order[1])
            elif record_index == 2:
                self.assertEqual(record['source'], sort_order[2])
            record_index += 1



if __name__ == "__main__":
    unittest.main(verbosity=2)
