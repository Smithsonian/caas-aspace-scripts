#!/usr/bin/env python

# This script takes a CSV of digital objects and deletes all agents, dates, extents, languages, notes, and subjects
# from the record and uploads it back to ArchivesSpace
import copy
import csv

from asnake.aspace import ASpace
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from collections import namedtuple
from loguru import logger
from pathlib import Path
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
            self.aspace_client = ASnakeClient(baseurl=aspace_api,
                                              username=aspace_un,
                                              password=aspace_pw)
            self.aspace_client.authorize()
        except ASnakeAuthError as e:
            print(f'Failed to authorize ASnake client. ERROR: {e}')
            logger.error(f'Failed to authorize ASnake client. ERROR: {e}')
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
            print(f'INFO: There are no repositories in the Archivesspace Instance: {self.repo_info}')
            logger.info(f'INFO: There are no repositories in the Archivesspace Instance: {self.repo_info}')


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
            print(f'ERROR: get_digitalobjects parameter not valid: {parameters}')  # TODO: write error printing/logging function
            logger.error(f'get_digitalobjects parameter not valid: {parameters}')
            raise ValueError
        else:
            if parameters[0] == 'all_ids' and type(parameters[1]) is not bool:
                print(f'ERROR: get_digitalobjects parameter not valid: {parameters}')
                logger.error(f'get_digitalobjects parameter not valid: {parameters}')
                raise ValueError
            elif parameters[0] == 'page' and type(parameters[1]) is not int:
                print(f'ERROR: get_digitalobjects parameter not valid: {parameters}')
                logger.error(f'get_digitalobjects parameter not valid: {parameters}')
                raise ValueError
            elif parameters[0] == 'id_set' and type(parameters[1]) is not str:  # TODO: how to handle id_set validation and multiple inputs
                print(f'ERROR: get_digitalobjects parameter not valid: {parameters}')
                logger.error(f'get_digitalobjects parameter not valid: {parameters}')
                raise ValueError
            else:
                digital_objects = self.aspace_client.get(f'{repository_uri}/digital_objects?{parameters[0]}={parameters[1]}').json()
                return digital_objects

    def update_object(self, object_uri, updated_json):
        """

        Args:
            object_uri (str): the original object's URI for posting to the client
            updated_json (dict): the updated metadata for the object

        Returns:
            update_message (dict): ArchivesSpace response
        """
        update_message = self.aspace.client.post(f'{object_uri}', json=updated_json).json()
        return update_message


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
        print(f'Failed to authorize ASnake client. ERROR: {e}')
        return ASnakeAuthError
    else:
        return client


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


def update_object(client, original_objecturi, new_object):
    """

    Args:
        client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API
        original_objecturi (str): the original object's URI for posting to the client
        new_object (dict): the updated metadata for the object

    Returns:
        update_message (dict): ArchivesSpace response
    """
    update_message = client.post(f'{original_objecturi}', json=new_object).json()
    return update_message


def run_script(missing_titles_csv):
    """
    Runs the functions of the script, taking a csv input containing all the URIs of objects with 'Missing Title' in
    their notes, parsing the notes and removing the title, then updating the resources and archival objects by posting
    to ASpace

    Args:
        missing_titles_csv (str): filepath for the missing titles csv listing all the URIs for resources or archival
    objects
    """
    client = client_login(as_api, as_un, as_pw)
    missingtitles = read_csv(missing_titles_csv)
    for mt_object in missingtitles:
        object_md = client.get(f'{mt_object['uri']}').json()
        if 'error' in object_md:
            logger.error(f'ERROR getting object metadata: {object_md}')
            print(f'ERROR getting object metadata: {object_md}')
        else:
            pass
            # updated_object = get_objects(object_md)
            # if updated_object.Status == "ERROR":
            #     logger.error(updated_object.Message)
            #     print(f'{updated_object.Status}: {updated_object.Message}')
            # elif updated_object.Status == "PASS":
            #     pass
            # else:
            #     aspace_response = update_object(client, object_md['uri'], updated_object.Message)
            #     if 'error' in aspace_response:
            #         logger.error(aspace_response)
            #         print(f'!!ERROR!!: {aspace_response}')
            #     else:
            #         logger.info(f'{aspace_response}')
            #         print(f'Updated object data: {aspace_response}')


if __name__ == "__main__":
    run_script(str(Path(f'../test_data/')))  # TODO: Fill out
