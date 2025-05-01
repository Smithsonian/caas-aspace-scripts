# This script updates existing subjects in bulk from a csv
import csv
import os
import sys

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

logger.remove()
log_path = Path('./logs', 'update_subjects_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

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

def read_csv(updated_subjects_csv):
    """
    Args:
        updated_subjects_csv (str): filepath for the subjects csv

    Returns:
        updated_subjects (list): a list of subjects to update and their metadata based on the csv contents
    """
    updated_subjects = []
    try:
        open_csv = open(updated_subjects_csv, 'r', encoding='UTF-8')
        updated_subjects = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return updated_subjects
    
def get_subject(client, existing_subject_id):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        existing_subject_id (str): id of the subject to be updated

    Returns:
        existing_subj (dict): the existing subject returned from ArchivesSpace's API
        None (NoneType): if problem retrieving existing subject
    """
    existing_subj = client.get(f'subjects/{existing_subject_id}').json()
    if 'error' in existing_subj:
        logger.error(f'ERROR getting existing subject {existing_subject_id}: {existing_subj}')
        print(f'ERROR getting existing subject {existing_subject_id}: {existing_subj}')
    else:
        return existing_subj
    
def build_subject(existing_subj, subj):
    """
    Builds out the updated subjects based on a mixture of existing subject content and csv content.

    Args:
        existing_subj (dict): Existing ArchivesSpace subject
        subj (dict): subject metadata from csv

    Returns:
        existing_subj (dict): updated subject ready to post to ArchivesSpace
    """
    existing_subj['terms'] = [
            {
                'term': subj['new_title'],
                'term_type': 'cultural_context',
                'vocabulary': '/vocabularies/1'

            }
        ]
    existing_subj['scope_note'] = subj['new_scope_note']
    existing_subj['external_ids'] = [
        {
            'external_id': subj['new_EMu_ID'],
            'source': 'EMu_ID'
        }
    ]
    return existing_subj

def update_subject(client, existing_subj_id, data):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        existing_subj_id (str): id of the subject to be updated
        data (dict): updated subject ready to post to ArchivesSpace
    
    Returns:
        update_message (dict): ArchivesSpace API response
    """
    update_message = client.post(f'subjects/{existing_subj_id}', json=data).json()
    if 'error' in update_message:
        logger.error(update_message)
        print(f'ERROR: {update_message}')
    else:
        logger.info(f'{update_message}')
        print(f'Updated object data: {update_message}')
    return update_message

def main(updated_subjects_csv):
    """
    Runs the functions of the script, collecting, building, then updating subject metadata in ArchivesSpace, printing
    error messages if they occur

    Takes a csv input of existing ASpace subjects to update with the following columns, at minimum:
        - aspace_subject_id
        - new_title
        - new_scope_note
        - new_EMu_ID

    Args:
        updated_subjects_csv (str): filepath for the subjects csv
    """
    client = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    updated_subjects = read_csv(updated_subjects_csv)
    for subj in updated_subjects:
        existing_subj_id = subj['aspace_subject_id']
        existing_subj = get_subject(client, existing_subj_id)
        if existing_subj is not None:
            data = build_subject(existing_subj, subj)
            update_subject(client, existing_subj_id, data)

# Call with `python update_subjects.py <filename>.csv`
if __name__ == "__main__":
    main(str(Path(f'{sys.argv[1]}')))