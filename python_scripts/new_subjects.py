# This script creates new subjects in bulk from a csv
import csv
import os
import sys

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

logger.remove()
log_path = Path(f'./logs', 'new_subjects_{time:YYYY-MM-DD}.log')
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

def read_csv(new_subjects_csv):
    """
    Args:
        new_subjects_csv (str): filepath for the subjects csv

    Returns:
        new_subjects (list): a list of new subjects and their metadata based on the csv contents
    """
    new_subjects = []
    try:
        open_csv = open(new_subjects_csv, 'r', encoding='UTF-8')
        new_subjects = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return new_subjects
    
def build_subject(subj):
    """
    Builds out the new subjects based on a mixture of csv content and hardcoded repository defaults.

    Several metadata elements are hard-coded to match the bespoke practices of NMAI, including:
        - term_type = cultural_context
        - source = 'nmaict'
        - unique EMu_IDs used to generate external_ids with a source of 'EMu_ID'

    Args:
        subj (dict): subject metadata from csv

    Returns:
        data (dict): new subject ready to post to ArchivesSpace
    """
    data = {}
    data['terms'] = [
        {
            'term': subj['new_title'],
            'term_type': 'cultural_context',
            'vocabulary': '/vocabularies/1'

        }
    ]
    data['scope_note'] = subj['new_scope_note']
    data['source'] = 'nmaict'
    data['external_ids'] = [
        {
            'external_id': subj['new_EMu_ID'],
            'source': 'EMu_ID'
        }
    ]
    data['vocabulary'] = '/vocabularies/1'

    return data
    
def create_subject(client, data):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        data (dict): new subject ready to post to ArchivesSpace
    
    Returns:
        create_message (dict): ArchivesSpace API response
    """
    create_message = client.post('/subjects', json=data).json()
    if 'error' in create_message:
        logger.error(create_message)
        print(f'ERROR: {create_message}')
    else:
        logger.info(f'{create_message}')
        print(f'Created object data: {create_message}')
    return create_message

def main(new_subjects_csv):
    """
    Runs the functions of the script, collecting, building, then posting subject metadata to ArchivesSpace, printing
    error messages if they occur

    Takes a csv input of potential new ASpace subjects with the following columns, at minimum:
        - new_title
        - new_scope_note
        - new_EMu_ID

    Args:
        new_subjects_csv (str): filepath for the subjects csv
    """
    client = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    new_subjects = read_csv(new_subjects_csv)
    for subj in new_subjects:
        data = build_subject(subj)
        create_subject(client, data)

# Call with `python new_subjects.py <filename>.csv`
if __name__ == "__main__":
    main(str(Path(f'{sys.argv[1]}')))
