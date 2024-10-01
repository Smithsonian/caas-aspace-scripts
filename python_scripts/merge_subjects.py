# This script merges two existing subjects identified in a provided csv
import csv
import sys

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from loguru import logger
from pathlib import Path
from secrets import *

logger.remove()
log_path = Path(f'./logs', 'merge_subjects_{time:YYYY-MM-DD}.log')
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
        logger.error(f'Failed to authorize ASnake client. ERROR: {e}')
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
        logger.error(f'ERROR getting existing subject: {existing_subj}')
        print(f'ERROR getting existing subject: {existing_subj}')
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
    """
    existing_title = get_subject(client, subj_id)['terms'][0]['term']
    return existing_title == subj_title
    
def merge_subject(client, destination_subj_uri, candidate_subj_uri):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        destination_subj_uri (str): uri of the destination/surviving subject
        candidate_subj_uri (str): uri of the canditate/removed subject
    
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
        print(f'!!ERROR!!: {merge_message}')
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
    client = client_login(as_api, as_un, as_pw)
    merge_subjects = read_csv(merge_subjects_csv)
    for subj in merge_subjects:
        destination_check = check_subject(client, subj['aspace_subject_id'], subj['title'])
        candidate_check = check_subject(client, subj['aspace_subject_id2'], subj['Merge into'])
        if destination_check and candidate_check:
            merge_subject(client, f'/subjects/{subj["aspace_subject_id"]}', f'/subjects/{subj["aspace_subject_id2"]}')
        else:
            logger.error(destination_check)
            logger.error(candidate_check)
            print(f'!!ERROR!!: Destination match is {destination_check} and Candidate match is {candidate_check}.')

# Call with `python merge_subjects.py <filename>.csv`
if __name__ == "__main__":
    main(str(Path(f'{sys.argv[1]}')))
