#!/usr/bin/env python

# This script iterates through all the digital objects in every repository in SI's ArchivesSpace instance - except Test,
# Training, and NMAH-AF, parses them for any data in the following fields: agents, dates, extents, languages, notes,
# and subjects, and then deletes any data within those fields except digitized date and uploads the updated digital
# object back to ArchivesSpace
import json
from copy import deepcopy
from http.client import HTTPException
from pathlib import Path

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from collections import namedtuple
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


    def get_objects(self, repository_uri, record_type, parameters = ('all_ids', True)):
        """
        Intakes a repository URI and returns all the digital object IDs as a list for that repository
        Args:
            repository_uri (str): the repository URI
            record_type (str): the type of record object you want to get (resources, archival_objects, digital_objects,
                accessions, etc.)
            parameters (tuple): Selected parameter and value: ('all_ids', 'True'), ('page', '#'), and
            (id_set, '1,2,3,etc.') Default is ('all_ids', 'True')

        Returns:
            digital_objects (list): all the digital object IDs

        """
        parameter_options = ['all_ids', 'page', 'id_set']
        if parameters[0] not in parameter_options:
            record_error('get_objects() - parameter not valid', parameters)
            raise ValueError
        else:
            if parameters[0] == 'all_ids' and type(parameters[1]) is not bool:
                record_error('get_objects() - parameter not valid', parameters)
                raise ValueError
            elif parameters[0] == 'page' and type(parameters[1]) is not int:
                record_error('get_objects() - parameter not valid', parameters)
                raise ValueError
            elif parameters[0] == 'id_set' and type(parameters[1]) is not str:  # TODO: how to handle id_set validation and multiple inputs
                record_error('get_objects() - parameter not valid', parameters)
                raise ValueError
            else:
                digital_objects = self.aspace_client.get(f'{repository_uri}/{record_type}?{parameters[0]}={parameters[1]}').json()
                return digital_objects

    def get_object(self, record_type, object_id, repo_uri = ''):
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
            record_error(f'get_object() - Unable to retrieve object', get_error)
        else:
            if 'error' in object_json:
                record_error(f'get_object() - Unable to retrieve object with provided URI', object_json)
            else:
                return object_json

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
        if 'error' in update_message:
            record_error('update_object() - Update failed due to following error', update_message)
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

# def read_csv(delete_domd_csv):
#     """
#     Takes a csv input of ASpace digital objects - ran from SQL query - and returns a list of dictionaries of all the
#     digital objects metadata
#
#     Args:
#         delete_domd_csv (str): filepath for the delete digital object metadata csv containing metadata for all digital
#         objects to edit
#
#     Returns:
#         digital_objects (list): a list of dictionaries for each column name (key) and row values (value)
#     """
#     digital_objects = []
#     try:
#         open_csv = open(delete_domd_csv, 'r', encoding='UTF-8')
#         digital_objects = csv.DictReader(open_csv)
#     except IOError as csverror:
#         logger.error(f'ERROR reading csv file: {csverror}')
#         print(f'ERROR reading csv file: {csverror}')
#     else:
#         return digital_objects


def parse_delete_fields(object_json):
    """
    Iterate through digital object JSON for specific fields and if the field is found, add it to a fields_to_delete list
    as a named tuple, with Field and Subrecord, returning the list

    Args:
        object_json (dict): metadata for the specific object in JSON

    Returns:
        fields_to_delete (list): list of named tuples (named DeleteField), with Field being the name of the field
            parsed (ex. dates, extents, etc.) and Subrecord being the dictionary subrecord of the field, with multiple
            subrecords added
    """
    fields_to_check = ['linked_agents', 'dates', 'extents', 'lang_materials', 'notes', 'subjects']
    fields_to_delete = []
    DeleteField = namedtuple('DeleteField', 'Field Subrecord')
    for field in fields_to_check:
        if field in object_json:
            if object_json[f'{field}']:
                for subrecord in object_json[f'{field}']:
                    if 'label' in subrecord and field == 'dates':
                        if not subrecord['label'] == 'digitized':
                            fields_to_delete.append(DeleteField(field, subrecord))
                    else:
                        fields_to_delete.append(DeleteField(field, subrecord))
    return fields_to_delete



def delete_field_info(object_json, field, subrecord):
    """
    Take the digital object JSON metadata and remove the given subrecord from the given field, returning the updated
    JSON

    Args:
        object_json (dict): metadata for the specific object in JSON
        field (str): the name of the field (key) to remove its data (value)
        subrecord (any): the subrecord for the field, ex. a single subrecord for dates if more than one subrecord exists

    Returns:
        updated_json (dict): updated metadata for the object in JSON with the data for the selected field deleted
    """
    updated_json = deepcopy(object_json)
    updated_json[field].remove(subrecord)
    return updated_json


def run_script():
    """
    Runs the functions of the script by creating an ArchivesSpacec class instance, getting the repository info for every
    repository, then all the digital object IDs per each repository, gets the JSON data for the digital object, deletes
    all information not contained within the Basic Information or File Version sections and posts the updated JSON to
    ArchivesSpace, saving the old JSON data in a separate file.
    """
    donotrun_repos = ['Test', 'TRAINING', 'NMAH-AF']
    original_do_json_data = []
    archivesspace_instance = ArchivesSpace(as_api_stag, as_un, as_pw)   # TODO: replace as_api_stag with as_api_prod
    archivesspace_instance.get_repo_info()
    for repo in archivesspace_instance.repo_info:
        if repo['repo_code'] not in donotrun_repos:
            all_digital_object_ids = archivesspace_instance.get_objects(repo['uri'], 'digital_objects')
            if len(all_digital_object_ids) > 0:
                for do_id in all_digital_object_ids:
                    digital_object_json = archivesspace_instance.get_object('digital_objects', do_id,
                                                                            repo['uri'])
                    delete_fields = parse_delete_fields(digital_object_json)
                    if delete_fields:
                        updated_digital_object_json = deepcopy(digital_object_json)
                        for field in delete_fields:
                            updated_digital_object_json = delete_field_info(updated_digital_object_json,
                                                                            field.Field,
                                                                            field.Subrecord)
                        if updated_digital_object_json:
                            original_do_json_data.append(digital_object_json)
                            # update_response = archivesspace_instance.update_object(updated_digital_object_json['uri'],
                            #                                                        updated_digital_object_json)
                            # print(f'Updated {updated_digital_object_json["uri"]}: {update_response}')
                            # logger.info(f'Updated {updated_digital_object_json["uri"]}: {update_response}')
    with open(f'../test_data/delete_dometadata_original_data.json', 'w', encoding='utf8') as org_data_file:
        json.dump(original_do_json_data, org_data_file, indent=4)
        org_data_file.close()


if __name__ == "__main__":
    run_script()
