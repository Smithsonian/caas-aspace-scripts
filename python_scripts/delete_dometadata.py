#!/usr/bin/env python

# This script takes a CSV of digital objects and deletes all agents, dates, extents, languages, notes, and subjects
# from the record and uploads it back to ArchivesSpace
import csv
from http.client import HTTPException
from pathlib import Path

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from loguru import logger

from secrets import *

logger.remove()
log_path = Path(f'../logs', 'delete_dometadata_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")


class ArchivesSpace:

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
        self.repo_info = self.aspace_client.get(f'repositories').json()
        if self.repo_info:
            return self.repo_info
        else:
            print(f'get_repo_info() - There are no repositories in the Archivesspace Instance: {self.repo_info}')
            logger.info(f'get_repo_info() - There are no repositories in the Archivesspace Instance: {self.repo_info}')


    def get_digitalobjects(self, repository_uri, parameters = ('all_ids', True)):
        """
        Intakes a repository URI and returns all the digital object IDs as a list for that repository
        Args:
            repository_uri (str): the repository URI
            parameters (tuple): Selected parameter and value: ('all_ids', 'True'), ('page', '#'), and
            (id_set, '1,2,3,etc.') Default is ('all_ids', 'True')

        Returns:
            digital_objects (list): all the digital object IDs

        """
        parameter_options = ['all_ids', 'page', 'id_set']
        if parameters[0] not in parameter_options:
            record_error('get_digitalobjects() - parameter not valid', parameters)
            raise ValueError
        else:
            if parameters[0] == 'all_ids' and type(parameters[1]) is not bool:
                record_error('get_digitalobjects() - parameter not valid', parameters)
                raise ValueError
            elif parameters[0] == 'page' and type(parameters[1]) is not int:
                record_error('get_digitalobjects() - parameter not valid', parameters)
                raise ValueError
            elif parameters[0] == 'id_set' and type(parameters[1]) is not str:  # TODO: how to handle id_set validation and multiple inputs
                record_error('get_digitalobjects() - parameter not valid', parameters)
                raise ValueError
            else:
                digital_objects = self.aspace_client.get(f'{repository_uri}/digital_objects?{parameters[0]}={parameters[1]}').json()
                return digital_objects

    def get_digitalobject(self, repo_uri, object_id):
        """
        Get and return a digital object JSON metadata from its URI

        Args:
            repo_uri (str): the repository ArchivesSpace URI
            object_id (int): the original object ArchivesSpace ID

        Returns:
            do_json (dict): the JSON metadata for a digital object
        """
        try:
            digital_object = self.aspace_client.get(f'{repo_uri}/digital_objects/{object_id}').json()
        except HTTPException as get_error:
            record_error(f'get_digitalobject() - Unable to retrieve digital object', get_error)
        else:
            if 'error' in digital_object:
                record_error(f'get_digitalobject() - Unable to retrieve digital object with provided URI',
                             digital_object)
            else:
                return digital_object

    def update_object(self, object_uri, updated_json):
        """
        Posts the updated JSON metadata for the given object_uri to ArchivesSpace

        Args:
            object_uri (str): the original object's URI for posting to the client
            updated_json (dict): the updated metadata for the object

        Returns:
            update_message (dict): ArchivesSpace response
        """
        update_message = self.aspace_client.post(f'{object_uri}', json=updated_json).json()
        return update_message


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

def read_csv(delete_domd_csv):
    """
    Takes a csv input of ASpace digital objects - ran from SQL query - and returns a list of dictionaries of all the
    digital objects metadata

    Args:
        delete_domd_csv (str): filepath for the delete digital object metadata csv containing metadata for all digital
        objects to edit

    Returns:
        digital_objects (list): a list of dictionaries for each column name (key) and row values (value)
    """
    digital_objects = []
    try:
        open_csv = open(delete_domd_csv, 'r', encoding='UTF-8')
        digital_objects = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return digital_objects


def delete_missingtitle(object_notes):
    """
    Iterate through all the notes of a specific object (resource or archival object) and return updated notes without
    'Missing Title' in notes list titles

    Args:
        object_notes (list): metadata for the specific object's notes (resource or archival_object)

    Returns:
        new_notes (list): updated notes metadata for object without 'Missing Title' in notes list titles or empty list
        if there are no notes found with 'Mising Title'
    """
    new_notes = []
    for note in object_notes:
        if note['jsonmodel_type'] == 'note_multipart':
            if 'subnotes' in note:
                for subnote in note['subnotes']:
                    if (subnote['jsonmodel_type'] == 'note_orderedlist' or
                            subnote['jsonmodel_type'] == 'note_definedlist' or
                            subnote['jsonmodel_type'] == 'note_chronology'):
                        if 'title' in subnote:
                            if subnote['title'] == 'Missing Title':
                                new_notes = object_notes
                                subnote.pop('title', None)
    return new_notes


def run_script(digital_objects_csv):
    """
    Runs the functions of the script, taking a csv input containing all the URIs of digital objects, gets the JSON data
    for the digital object, deletes all information not contained within the Basic Information or File Version sections
    and posts the updated JSON to ArchivesSpace

    Args:
        digital_objects_csv (str): filepath for the digital objects csv listing all the URIs for digital objects in an
        ArchivesSpace instance
    """
    archivesspace_instance = ArchivesSpace(as_api_stag, as_un, as_pw)
    archivesspace_instance.get_repo_info()
    # digitalobjects = read_csv(digital_objects_csv)  TODO: fill this out once we have a CSV - use get_digitalobjects in the meantime
    no_repos = ['Test', 'TRAINING', 'NMAH-AF']
    for repo in archivesspace_instance.repo_info:
        if not repo['repo_code'] in no_repos:
            all_digital_object_ids = archivesspace_instance.get_digitalobjects(repo['uri'])
            # print(f'{repo['repo_code']}: {len(all_digital_object_ids)}')
            if len(all_digital_object_ids) > 0:
                digital_object_json = archivesspace_instance.get_digitalobject(repo['uri'], all_digital_object_ids[0])
                if digital_object_json['linked_agents'] or digital_object_json['dates'] or digital_object_json['extents'] or digital_object_json['lang_materials'] or digital_object_json['notes'] or digital_object_json['subjects']:
                    print(digital_object_json)


if __name__ == "__main__":
    run_script(str(Path(f'../test_data/')))  # TODO: Fill out
