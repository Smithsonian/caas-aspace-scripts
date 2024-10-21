#!/usr/bin/env python

# This script consists of unittests for update_resids.py
import contextlib
import io
import os
import unittest

from python_scripts.eepa_cameroonreport import *
from secrets import *
from test_data.eepacameroon_testdata import *


class TestClientLogin(unittest.TestCase):

    def test_default_connection(self):
        """Test using default connection info found in secrets.py"""
        self.local_aspace = client_login(as_api_stag, as_un, as_pw)
        self.assertIsInstance(self.local_aspace, ASnakeClient)

    def test_error_connection(self):
        """Test using garbage input for ASnakeAuthError return"""
        self.local_aspace = client_login("https://www.cnn.com", "garbage", "garbage")
        self.assertEqual(self.local_aspace, ASnakeAuthError)

class TestReadCSV(unittest.TestCase):

    def test_good_csv(self):
        test_camerooncsvs = read_csv(str(Path(f'../test_data/EEPA_Cameroon_Reports/'
                                             f'Cameroon - List of Archival Collection- URI.csv')))
        self.assertIsNotNone(test_camerooncsvs)
        for row in test_camerooncsvs:
            self.assertIsInstance(row, dict)

    def test_bad_csv(self):
        test_missingcsv = read_csv(str(Path(f'../test_data/EEPA_Cameroon_Reports/fake.csv')))
        self.assertRaises(FileNotFoundError)
        self.assertEqual(test_missingcsv, None)


class TestWriteCSV(unittest.TestCase):

    def test_good_csv(self):
        old_test_file = str(Path(f'../test_data/EEPA_Cameroon_Reports/Cameroon - List of Archival Collection- URI.csv'))
        new_test_file = str(Path(f'../test_data/EEPA_Cameroon_Reports/Cameroon - List of Archival Collection- '
                                 f'Abstracts.csv'))
        test_values = ['Abstract/Scope']
        for row in open(old_test_file):
            test_values.append('blahblahblah')
        write_csv(old_test_file, new_test_file, test_values)
        self.assertTrue(os.path.isfile(f'../test_data/EEPA_Cameroon_Reports/'
                                           f'Cameroon - List of Archival Collection- Abstracts.csv'))
        with open(new_test_file, 'r', newline='', encoding='utf-8') as readcsv:
            csvreader = csv.reader(readcsv)
            row_count = 0
            for row in csvreader:
                if row_count == 0:
                    self.assertEqual(row[-1], 'Abstract/Scope')
                    row_count += 1
                else:
                    self.assertEqual(row[-1], 'blahblahblah')
                    row_count += 1
        os.remove(new_test_file)

    def test_bad_csv(self):
        old_test_file = str(Path(f'../test_data/EEPA_Cameroon_Reports/DOESNOTEXIST.csv'))
        new_test_file = str(Path(f'../test_data/EEPA_Cameroon_Reports/BADOUTPUT.csv'))
        test_values = ['Abstract/Scope', 'blahblahblah']
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            write_csv(old_test_file, new_test_file, test_values)
        self.assertTrue(r"""Error when reading/writing to CSV: [Errno 2] No such file or directory: '..\\test_data\\EEPA_Cameroon_Reports\\DOESNOTEXIST.csv'""" in f.getvalue())



class TestGetResourceMetadata(unittest.TestCase):

    def test_good_resource(self):
        self.local_aspace = client_login(as_api_stag, as_un, as_pw)
        test_resource_uri = f'/repositories/20/resources/4804'  # Has Abstract and Scope and Contents
        test_resource_json = get_resource_metadata(test_resource_uri, self.local_aspace)
        self.assertIsInstance(test_resource_json, dict)
        self.assertEqual(test_resource_json['title'], f'World War One Theater Lantern Slides')


    def test_bad_uri(self):
        self.local_aspace = client_login(as_api_stag, as_un, as_pw)
        test_bad_uri = f'/repositories/20/resources/4804a'
        get_resource_metadata(test_bad_uri, self.local_aspace)
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            get_resource_metadata(test_bad_uri, self.local_aspace)
        self.assertTrue('''ERROR getting object metadata: {'error': {'id': ["Wanted type Integer but got '4804a'"]}}'''
                        in f.getvalue())


class TestFindAbstractScope(unittest.TestCase):

    def test_abstract_only(self):
        abstract_only_json = find_abstract_scope(test_abstract_only_json)
        self.assertIsInstance(abstract_only_json, str)
        self.assertEqual(abstract_only_json, 'Photographs taken by Klara Farkas in Ethiopia in 1971.')

    def test_scope_only(self):
        scope_only_json = find_abstract_scope(test_scope_only_json)
        self.assertIsInstance(scope_only_json, str)
        self.assertEqual(scope_only_json, 'Photographic print of Eliot Elisofon accepting an award on March 1, '
                                          '1953 from Modern Photography for "Outstanding Color Photography" in the film '
                                          'Moulin Rouge.')

    def test_no_note(self):
        no_scope_abstract_json = find_abstract_scope(test_no_abstract_scope_json)
        self.assertIsInstance(no_scope_abstract_json, str)
        self.assertEqual(no_scope_abstract_json, '')
