#!/usr/bin/env python

# This script consists of unittests for report_grouppermissions.py
import copy
import json
import contextlib
import io
import os
import unittest

import mysql.connector
import openpyxl
import openpyxl.utils.exceptions

from python_scripts.report_grouppermissions import *
from test_data.dometadata_testdata import *
from secrets import *

class TestASpaceDatabaseClass(unittest.TestCase):

    def test_good_connection(self):
        """
        Tests connection with good credentials as founds within the secrets.py file
        """
        test_dbconnection = ASpaceDatabase(as_dbstag_un, as_dbstag_pw, as_dbstag_host, as_dbstag_database,
                                           as_dbstag_port)
        self.assertIsNotNone(test_dbconnection.connection)
        self.assertIsNotNone(test_dbconnection.cursor)

    def test_bad_connection(self):
        """
        Tests that an error is raised with making a connection with a bad username and password using the database found
        in the secrets.py file
        """
        with self.assertRaises(mysql.Error):
            ASpaceDatabase('bad_un', 'bad_pw', 'bad_host', as_dbstag_database,
                           as_dbstag_port)

    def test_good_query(self):
        """
        Tests that the query_database() function returns a list of users from an ASpace database
        """
        test_query = ('SELECT name, username FROM user')
        test_connection = ASpaceDatabase(as_dbstag_un, as_dbstag_pw, as_dbstag_host, as_dbstag_database,
                                           as_dbstag_port)
        test_results = test_connection.query_database(test_query)
        self.assertIsNotNone(test_results)
        self.assertIsInstance(test_results, list)

    def test_bad_query(self):
        """
        Tests that a badly formatted SQL query will raise a mysql.Error
        """
        test_bad_query = ('SELECT nothing, username FROM user')
        test_connection = ASpaceDatabase(as_dbstag_un, as_dbstag_pw, as_dbstag_host, as_dbstag_database,
                                           as_dbstag_port)
        with self.assertRaises(mysql.Error):
            test_connection.query_database(test_bad_query)

class TestSpreadsheetClass(unittest.TestCase):

    def test_generate_workbook_good(self):
        """
        Tests generating an openpyxl Workbook instance and assigns it as a Spreadsheet instance variable
        """
        test_spreadsheet_filepath = str(Path('../test_data', f'report_grouppermissions_{str(date.today())}.xlsx'))
        test_spreadsheet = Spreadsheet(test_spreadsheet_filepath)
        self.assertIsInstance(test_spreadsheet, Spreadsheet)
        self.assertIsInstance(test_spreadsheet.wb, openpyxl.Workbook)
        os.remove(test_spreadsheet_filepath)

    def test_generate_workbook_bad(self):
        """
        Tests generating an openpyxl Workbook instance with a bad filepath to make sure it raises an error
        """
        test_spreadsheet_filepath = str(f'//bad_filepath')
        with self.assertRaises(FileNotFoundError):
            Spreadsheet(test_spreadsheet_filepath)

    def test_create_sheet(self):
        test_spreadsheet_filepath = str(Path('../test_data', f'report_grouppermissions_{str(date.today())}.xlsx'))
        test_spreadsheet = Spreadsheet(test_spreadsheet_filepath)
        test_sheetname = 'test'
        test_spreadsheet.create_sheet(test_sheetname)

        test_sheetnames = test_spreadsheet.wb.sheetnames
        self.assertIn("test", test_sheetnames)
        self.assertIn('test', test_spreadsheet.sheets)
        test_spreadsheet.wb.close()
        os.remove(test_spreadsheet_filepath)

    def test_create_sheet_error(self):
        test_spreadsheet_filepath = str(Path('../test_data', f'report_grouppermissions_{str(date.today())}.xlsx'))
        test_spreadsheet = Spreadsheet(test_spreadsheet_filepath)
        test_sheetname = 'my:test:sheet'
        with self.assertRaises(ValueError):
            test_spreadsheet.create_sheet(test_sheetname)
        test_spreadsheet.wb.close()
        os.remove(test_spreadsheet_filepath)


    def test_write_headers(self):
        """
        Test write_headers() function by writing a list of test headers to a spreadsheet and assert that those test
        header values exist in the spreadsheet.
        """
        test_headers = ["test_header_1", "test_header_2", "test_header_3"]
        test_spreadsheet_filepath = str(Path('../test_data', f'report_grouppermissions_{str(date.today())}.xlsx'))
        test_spreadsheet = Spreadsheet(test_spreadsheet_filepath)
        test_worksheet = test_spreadsheet.create_sheet('test')
        test_spreadsheet.write_headers(test_worksheet, test_headers)

        if "test" in test_spreadsheet.wb.sheetnames:
            test_sheet = test_spreadsheet.wb["test"]
            for row in test_sheet.iter_rows(max_row=1, max_col=3):
                for cell in row:
                    self.assertIn(cell.value, test_headers)
        test_spreadsheet.wb.close()
        os.remove(test_spreadsheet_filepath)

class TestRecordError(unittest.TestCase):

    def test_str_input(self):
        """
        Tests that a string input for the record_error() status_input variable properly prints
        """
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            record_error('This is a test error', 'Error 404 - page not found')
        self.assertTrue(r"""This is a test error: Error 404 - page not found""" in f.getvalue())

    def test_tuple_input(self):
        """
        Tests that a tuple input for the record_error() status_input variable properly prints
        """
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            record_error('This is a test error', ('test_this', 'and_this'))
        self.assertTrue(r"""This is a test error: ('test_this', 'and_this')""" in f.getvalue())

    def test_bool_input(self):
        """
        Tests that a boolean input for the record_error() status_input variable properly prints
        """
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            record_error('This is a test error', False)
        self.assertTrue(r"""This is a test error: False""" in f.getvalue())

