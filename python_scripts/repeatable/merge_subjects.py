# This script merges two existing subjects identified in a provided csv
import csv
import os
import sys

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

logger.remove()
log_path = Path('./logs', 'merge_subjects_{time:YYYY-MM-DD}.log')
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

def read_csv(merge_subjects_csv):
    """
    Args:
        merge_subjects_csv (str): filepath for the subjects csv

    Returns:
        merge_subjects (list): a list of subjects to be merged
    """
    merge_subjects = []
    try:
        open_csv = open(merge_subjects_csv, 'r', encoding='UTF-8')
        merge_subjects = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return merge_subjects

def get_subject(client, existing_subject_id):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        existing_subject_id (str): id of the subject to be retrieved

    Returns:
        existing_subj (dict): the existing subject returned from ArchivesSpace's API
    """
    existing_subj = client.get(f'subjects/{existing_subject_id}').json()
    if 'error' in existing_subj:
        logger.error(f'ERROR getting existing subject {existing_subject_id}: {existing_subj}')
        print(f'ERROR getting existing subject {existing_subject_id}: {existing_subj}')
    return existing_subj
    
def check_subject(client, subj_id, subj_title):
    """
    Checks that the subject returned matches the title/term in the provided csv

    Args:
        client (ASnake.client object): client object from ASnake.client
        subj_id (dict): subject id from csv
        subj_title (dict): subject title from csv

    Returns:
        match (bool): True/False if subject matches
        None (NoneType): When an error getting the subject
    """
    existing_subj = get_subject(client, subj_id)
    if 'error' not in existing_subj:
        existing_title = existing_subj['terms'][0]['term']
        return existing_title == subj_title
    
def merge_subject(client, destination_subj_uri, candidate_subj_uri):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        destination_subj_uri (str): uri of the destination/surviving subject
        candidate_subj_uri (str): uri of the candidate/removed subject
    
    Returns:
        merge_message (dict): ArchivesSpace API response
    """
    data = {
        'uri': 'merge_requests/subject',
        'target': {
            'ref': destination_subj_uri
        },
        'victims': [
            {
                'ref': candidate_subj_uri
            }
        ]
    }
    merge_message = client.post('/merge_requests/subject', json=data).json()
    if 'error' in merge_message:
        logger.error(merge_message)
        print(f'ERROR: {merge_message}')
    else:
        logger.info(f'{merge_message}')
        print(f'Merged object data: {merge_message}')
    return merge_message

def main(merge_subjects_csv):
    """
    Runs the functions of the script, collecting, checking, then merging subject metadata in ArchivesSpace, printing
    error messages if they occur

    Takes a csv input of ASpace subjects to be merged with the following columns, at minimum:
        - aspace_subject_id - id of the merge destination/subject to be retained
        - title - title of the merge destination/subject to be retained
        - aspace_subject_id2 - id of the merge candidate/subject to be removed
        - Merge into - title of the merge candidate/subject to be removed

    Args:
        merge_subjects_csv (str): filepath for the subjects csv
    """
    client = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    merge_subjects = read_csv(merge_subjects_csv)
    for subj in merge_subjects:
        destination_id = subj['aspace_subject_id2']
        candidate_id = subj['aspace_subject_id']
        destination_match = check_subject(client, destination_id, subj['Merge into'])
        candidate_match = check_subject(client, candidate_id, subj['title'])
        if destination_match is not None and candidate_match is not None:
            if destination_match and candidate_match:
                merge_subject(client, f'/subjects/{subj["aspace_subject_id2"]}', f'/subjects/{subj["aspace_subject_id"]}')
            elif not destination_match and candidate_match:
                logger.error(f'ERROR: Destination subject id and title do not match for subject {destination_id}.')
                print(f'ERROR: Destination subject id and title do not match for subject {destination_id}.')
            elif destination_match and not candidate_match:
                logger.error(f'ERROR: Candidate subject id and title do not match for subject {candidate_id}.')
                print(f'ERROR: Candidate subject id and title do not match for subject {candidate_id}.')
            elif not destination_match and not candidate_match:
                logger.error(f'ERROR: Destination and candidate subject ids and titles do not match for ids {destination_id} and {candidate_id}.')
                print(f'ERROR: Destination and candidate subject ids and titles do not match for ids {destination_id} and {candidate_id}.')

# Call with `python merge_subjects.py <filename>.csv`
if __name__ == "__main__":
    main(str(Path(f'{sys.argv[1]}')))
