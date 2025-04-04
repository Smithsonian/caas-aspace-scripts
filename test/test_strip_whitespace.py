# This script consists of unittests for update_fileuri.py
import unittest

from python_scripts.repeatable.strip_whitespace import *

sample_json = {
    "lock_version": 2,
    "title": "Test resource 7\n\n",
    "publish": False
}
sample_nested_json = {
    "lock_version": 3,
    "digital_object_id": "12345",
    "title": "Example DO",
    "publish": False,
    "file_versions": [
        {
            "lock_version": 0,
            "file_uri": "http://example.com\n\n",
            "publish": False
        }
    ]
}

class TestStripWhitespace(unittest.TestCase):

    def test_first_level(self):
        """Tests that whitespace replacement at the primary object level is successful"""
        self.assertIn('\n\n', sample_json['title'])
        test_response = strip_whitespace(sample_json, 'title', '')
        self.assertIsInstance(test_response, dict)
        self.assertNotIn('error', test_response)
        self.assertNotIn('\n\n', test_response['title'])

    def test_second_level(self):
        """Tests that whitespace replacement in a nested object is successful"""
        self.assertIn('\n\n', sample_nested_json['file_versions'][0]['file_uri'])
        test_response = strip_whitespace(sample_nested_json, 'file_versions', 'file_uri')
        self.assertIsInstance(test_response, dict)
        self.assertNotIn('error', test_response)
        self.assertNotIn('\n\n', test_response['file_versions'][0]['file_uri'])

    def test_missing_field(self):
        """Tests that a missing field leads to an error"""
        test_response = strip_whitespace(sample_json, 'missing', '')
        self.assertIsNone(test_response)

if __name__ == "__main__":
    unittest.main(verbosity=2)
