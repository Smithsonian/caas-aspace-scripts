#!/usr/bin/env python
from http.client import HTTPException

import mysql.connector as mysql
import csv
import jsonlines
import requests

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from jsonlines import InvalidLineError
from loguru import logger
from mysql.connector import errorcode


class ASpaceAPI:

    def __init__(self, aspace_api, aspace_un, aspace_pw):
        """
        Establishes connection to ASnakeClient and runs queries to the ArchivesSpace API

        Args:
            aspace_api (str): ArchivesSpace API URL
            aspace_un (str): ArchivesSpace username - admin rights preferred
            aspace_pw (str): ArchivesSpace password
        """

        try:
            self.aspace_client = ASnakeClient(baseurl=aspace_api, username=aspace_un, password=aspace_pw)
            self.aspace_client.authorize()
        except ASnakeAuthError as e:
            record_error('ArchivesSpace __init__() - Failed to authorize ASnake client', e)
            raise ASnakeAuthError
        self.repo_info = []

    def get_repo_info(self):
        """
        Gets all the repository information for an ArchivesSpace instance in a list and assigns it to self.repo_info

        Returns:
            self.repo_info (list): a list of dictionaries containing all the repository information for an ArchivesSpace
            instance
        """
        self.repo_info = self.aspace_client.get('repositories').json()
        if self.repo_info:
            return self.repo_info
        print(f'get_repo_info() - There are no repositories in the Archivesspace Instance: {self.repo_info}')
        logger.info(f'get_repo_info() - There are no repositories in the Archivesspace Instance: {self.repo_info}')

    def get_objects(self, repository_uri, record_type, parameters=('all_ids', True)):
        """
        Intakes a repository URI and returns all the digital object IDs as a list for that repository

        Args:
            repository_uri (str): the repository URI
            record_type (str): the type of record object you want to get (resources, archival_objects, digital_objects,
                accessions, etc.)
            parameters (tuple): Selected parameter and value: ('all_ids', 'True'), ('page', '#'), and
            ('id_set',' [1,2,3,etc.]) Default is ('all_ids', 'True')

        Returns:
            digital_objects (list): all the digital object IDs
        """
        parameter_options = ['all_ids', 'page', 'id_set']
        if parameters[0] not in parameter_options:
            record_error('get_objects() - parameter not valid', parameters)
            raise ValueError
        if parameters[0] == 'all_ids' and not isinstance(parameters[1], bool):
            record_error('get_objects() - parameter not valid', parameters)
            raise ValueError
        if parameters[0] == 'page' and not isinstance(parameters[1], int):
            record_error('get_objects() - parameter not valid', parameters)
            raise ValueError
        if parameters[0] == 'id_set' and not isinstance(parameters[1], list):
            record_error('get_objects() - parameter not valid', parameters)
            raise ValueError
        if isinstance(parameters[1], list):
            digital_objects = []
            for identifier in parameters[1]:
                digital_objects.append(self.aspace_client.get(
                    f'{repository_uri}/{record_type}?{parameters[0]}={str(identifier)}').json())
        else:
            digital_objects = self.aspace_client.get(
                f'{repository_uri}/{record_type}?{parameters[0]}={parameters[1]}').json()
        return digital_objects

    def get_object(self, record_type, object_id, repo_uri=''):
        """
        Get and return a digital object JSON metadata from its URI

        Args:
            record_type (str): the type of record object you want to get (resources, archival_objects, digital_objects,
                accessions, etc.)
            object_id (int): the original object ArchivesSpace ID
            repo_uri (str): the repository ArchivesSpace URI including ending forward slash, default is None

        Returns:
            do_json (dict): the JSON metadata for a digital object
        """
        try:
            object_json = self.aspace_client.get(f'{repo_uri}/{record_type}/{object_id}').json()
        except HTTPException as get_error:
            record_error(f'get_object() - Unable to retrieve object {repo_uri}/{record_type}/{object_id}',
                         get_error)
        else:
            if 'error' in object_json:
                record_error(f'get_object() - Unable to retrieve object with provided URI: '
                             f'{repo_uri}/{record_type}/{object_id}',
                             object_json)
            else:
                return object_json

    def update_object(self, object_uri, updated_json):
        """
        Posts the updated JSON metadata for the given object_uri to ArchivesSpace

        Args:
            object_uri (str): the original object's URI for posting to the client
            updated_json (dict): the updated metadata for the object

        Returns:
            update_message (dict): ArchivesSpace response or None if an error was encountered and logged
        """
        update_message = self.aspace_client.post(f'{object_uri}', json=updated_json).json()
        if 'error' in update_message:
            record_error('update_object() - Update failed due to following error', update_message)
        else:
            return update_message

    def update_suppression(self, object_uri, suppression):
        """
        Suppresses or unsuppresses the given object_uri in ArchivesSpace

        Args:
            object_uri (str): the original object's URI for posting to the client
            suppression (bool): to suppress the object, set to True. To unsuppress, set to False

        Returns:
            update_message (dict): ArchivesSpace response or None if an error was encountered and logged
        """
        suppress_message = self.aspace_client.post(f'{object_uri}/suppressed',
                                                   params={"suppressed": suppression}).json()
        if 'error' in suppress_message:
            record_error('update_suppression() - Suppression failed due to following error', suppress_message)
        else:
            return suppress_message

    def delete_object(self, object_uri):
        """
        Deletes the given object from ArchivesSpace, given the object's URI. WARNING: deletions in ArchivesSpace are
        permanent!

        Args:
            object_uri (str): the object's URI for deletion

        Returns:
            update_message (dict): ArchivesSpace response or None if an error was encountered and logged
        """
        delete_message = self.aspace_client.delete(f'{object_uri}').json()
        if 'error' in delete_message:
            record_error('delete_object() - Delete failed due to following error', delete_message)
        else:
            return delete_message


class ASpaceDatabase:

    def __init__(self, as_db_un, as_db_pw, as_db_host, as_db_name, as_db_port):
        """
        Handles the connection to and data retrieval from the ArchivesSpace database

        Args:
            as_db_un (str): the username for the account to connect to the ArchivesSpace database
            as_db_pw (str): the password for the account to connect to the ArchivesSpace database
            as_db_host (str): the hostname for the ArchivesSpace database
            as_db_name (str): the name of the ArchivesSpace database
            as_db_port (int): the port number of the ArchivesSpace database
        """
        self.aspace_username = as_db_un
        self.aspace_password = as_db_pw
        self.aspace_host = as_db_host
        self.aspace_name = as_db_name
        self.aspace_port = as_db_port
        self.connection, self.cursor = self.connect_db()

    def connect_db(self):
        """
        Connects to the ArchivesSpace test database with credentials provided in local secrets.py file

        Returns:
             test_connect (mysql.connection): The connection to the database
             test_cursor (mysql.connection.cursor): The cursor of results for the database
        """

        try:
            self.connection = mysql.connect(user=self.aspace_username,
                                            password=self.aspace_password,
                                            host=self.aspace_host,
                                            database=self.aspace_name,
                                            port=self.aspace_port)
        except mysql.Error as error:
            if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                record_error('connect_db() - Failed to authorize username/password', error)
                raise error
            elif error.errno == errorcode.ER_BAD_DB_ERROR:
                record_error('connect_db() - Database does not exist', error)
                raise error
            else:
                record_error('connect_db() - Other error when connecting to the database', error)
                raise error
        else:
            self.cursor = self.connection.cursor()
            return self.connection, self.cursor

    def query_database(self, statement):
        """
        Runs a query on the database

        Args:
            statement (str): The MySQL statement to run against the database

        Returns:
            results (list): Results of the returned query as a list of tuples
        """
        try:
            self.cursor.execute(statement)
        except mysql.Error as error:
            record_error('query_database() - SQL query was invalid', error)
            raise error
        else:
            results = self.cursor.fetchall()
        return results

    def close_connection(self):
        """
        Closes the cursor and connection to the ArchivesSpace database
        """
        self.cursor.close()
        self.connection.close()


def client_login(as_api, as_un, as_pw):
    """
    Login to the ArchivesSnake client and return client

    Args:
        as_api (str): ArchivesSpace API URL
        as_un (str): ArchivesSpace username - admin rights preferred
        as_pw (str): ArchivesSpace password

    Returns:
        client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API
    """
    client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)

    try:
        client.authorize()
    except ASnakeAuthError as e:
        print(f'ERROR authorizing ASnake client: {e}')
        logger.error(f'ERROR authorizing ASnake client: {e}')
        return ASnakeAuthError
    else:
        return client


def read_csv(csv_file):
    """
    Args:
        csv_file (str): filepath for the subjects csv

    Returns:
        csv_dict (list): a list of subjects to update and their metadata based on the csv contents
    """
    try:
        open_csv = open(csv_file, 'r', encoding='UTF-8')
        csv_dict = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return csv_dict


def check_url(url):
    """
    Args:
        url (str): uri to be checked

    Returns:
        status (str): status of the request
    """
    try:
        response = requests.head(url)
        if response.status_code == 200:
            return True
        else:
            logger.error(f'ERROR with requested url: {url}.  Status code: {response.status_code}.')
            print(f'ERROR with requested url: {url}.  Status code: {response.status_code}.')
    except requests.exceptions.RequestException as e:
        logger.error(f'ERROR fetching uri: {e}')
        print(f'ERROR fetching uri: {e}')


def record_error(message, status_input):
    """
    Prints and logs an error message and the code/parameters causing the error

    Args:
        message (str): message to prefix the error code
        status_input (str, tuple, bool): error code or input parameters producing the error
    """
    try:
        print(f'{message}: {status_input}')
        logger.error(f'{message}: {status_input}')
    except TypeError as input_error:
        print(f'record_error() - Input is invalid for recording error: {input_error}')
        logger.error(f'record_error() - Input is invalid for recording error: {input_error}')


def write_to_file(filepath, write_data):
    """
    Writes or appends JSON data to a specified file using jsonlines
    Args:
        filepath (str): the path of the file being written to
        write_data (str): the data to be written on the given filepath
    """
    try:
        with jsonlines.open(filepath, mode='a') as org_data_file:
            try:
                org_data_file.write(write_data)
            except InvalidLineError as bad_write_error:
                record_error('write_to_file() - Unable to write data to file', bad_write_error)
        org_data_file.close()
    except (FileNotFoundError, PermissionError, OSError) as write_file_error:
        record_error('write_to_file() - Unable to open or access jsonl file', write_file_error)
