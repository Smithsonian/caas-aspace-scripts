#!/usr/bin/env python

# This script collects all resources and archival objects from every repository, checks their notes for lists and
# 'Missing Title' in the list title, removes the title and updates to ArchivesSpace
import copy
import csv

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from collections import namedtuple
from loguru import logger
from pathlib import Path
from secrets import *


logger.remove()
log_path = Path('../../logs', 'remove-missingtitles_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")


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


def read_csv(missing_titles_csv):
    """
    Takes a csv input of ASpace objects with "Missing Title" in them - ran from SQL query - and returns a list of all
    dictionaries of all the objects metadata, including their identifiers, repository ID, ASpace ID, and URI

    Args:
        missing_titles_csv (str): filepath for the missing titles csv listing metadata for resources or archival
    objects

    Returns:
        missingtitle_objects (list): a list of URIs (dict) with "Missing Title" in their notes
    """
    missingtitle_objects = []
    try:
        open_csv = open(missing_titles_csv, 'r', encoding='UTF-8')
        missingtitle_objects = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return missingtitle_objects


def get_objects(object_metadata, test=""):
    """
    Iterate through an object (resource or archival object) in a given repository and return new object without
    'Missing Title' in notes lists

    Args:
        object_metadata (dict): resource or archival object metadata
        test (str): if using unittests to record in log file, indicate with string input, default is empty string

    Returns:
        new_obj (tuple): returns ERROR, PASS, or UPDATED, then the message or new object
    """
    Update = namedtuple('Update', 'Status Message')
    new_object = copy.deepcopy(object_metadata)
    if 'notes' in object_metadata:
        if bool(object_metadata['notes']) is True:
            new_obj_notes = delete_missingtitle(new_object['notes'])
            if new_obj_notes:
                logger.info(f'{test}Old object metadata: {object_metadata}')
                new_object['notes'] = new_obj_notes
                logger.info(f'{test}New object metadata: {new_object}')
                new_obj = Update('UPDATED', new_object)
                return new_obj
            else:
                new_obj = Update('PASS', f'No title in {object_metadata["title"]}')
                return new_obj
        else:
            new_obj = Update('PASS', f'No notes with content in {object_metadata["title"]}')
            return new_obj
    else:
        new_obj = Update('PASS', f'No notes in {object_metadata["title"]}')
        return new_obj


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
    client = client_login(as_api_stag, as_un, as_pw)   # TODO: replace as_api_stag with as_api_prod
    missingtitles = read_csv(missing_titles_csv)
    for mt_object in missingtitles:
        object_md = client.get(f'{mt_object['uri']}').json()
        if 'error' in object_md:
            logger.error(f'ERROR getting object metadata: {object_md}')
            print(f'ERROR getting object metadata: {object_md}')
        else:
            updated_object = get_objects(object_md)
            if updated_object.Status == "ERROR":
                logger.error(updated_object.Message)
                print(f'{updated_object.Status}: {updated_object.Message}')
            elif updated_object.Status == "PASS":
                pass
            else:
                aspace_response = update_object(client, object_md['uri'], updated_object.Message)
                if 'error' in aspace_response:
                    logger.error(aspace_response)
                    print(f'!!ERROR!!: {aspace_response}')
                else:
                    logger.info(f'{aspace_response}')
                    print(f'Updated object data: {aspace_response}')


if __name__ == "__main__":
    run_script(str(Path('../test_data/MissingTitles_BeGone.csv')))
    print('TESTING')
