#!/usr/bin/env python

# This script updates digital object file_uri's based on a provided CSV.  For help on available arguments and options:
# `python repeatable/update_fileuri.py -h`.
import argparse
import os
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path
from python_scripts.utilities import check_url, client_login, read_csv

# Logging
logger.remove()
log_path = Path('./logs', 'update_fileuri_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to csv input file", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()
    
def get_digital_object(client, repo_id, digital_object_id):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        repo_id (str): id of the digital object's repository
        digital_object_id (str): id of the digital object to be updated

    Returns:
        existing_digital_object (dict): the existing digital object returned from ArchivesSpace's API
        None (NoneType): if problem retrieving existing digital object
    """
    existing_digital_object = client.get(f'/repositories/{repo_id}/digital_objects/{digital_object_id}').json()
    if 'error' in existing_digital_object:
        logger.error(f'ERROR getting existing digital object {digital_object_id}: {existing_digital_object}')
        print(f'ERROR getting existing digital object {digital_object_id}: {existing_digital_object}')
    else:
        return existing_digital_object
    
def build_digital_object(do, new_uri):
    """
    Builds out the updated digital object with new uri from csv.

    Args:
        do (dict): Existing ArchivesSpace digital object
        new_uri (str): new uri from csv

    Returns:
        do (dict): updated digital object ready to post to ArchivesSpace
    """
    if do['file_versions'][0]['file_uri'].endswith('.pdf'):
        do['file_versions'][0]['use_statement'] = 'application-pdf'
    if do['file_versions'][0]['file_uri'].endswith('.mp3'):
        do['file_versions'][0]['use_statement'] = 'audio-service'
    do['file_versions'][0]['file_uri'] = new_uri

    return do

def update_digital_object(client, repo_id, digital_object_id, data):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        digital_object_id (str): id of the digital object to be updated
        data (dict): updated digital object ready to post to ArchivesSpace
    
    Returns:
        update_message (dict): ArchivesSpace API response
    """
    update_message = client.post(f'repositories/{repo_id}/digital_objects/{digital_object_id}', json=data).json()
    if 'error' in update_message:
        logger.error(update_message)
        print(f'ERROR: {update_message}')
    else:
        logger.info(f'{update_message}')
        print(f'Updated object data: {update_message}')

    return update_message

def main(updated_file_uri_csv, dry_run):
    """
    Runs the functions of the script, collecting, building, then updating digital object metadata in ArchivesSpace, printing
    error messages if they occur

    Takes a csv input of existing ASpace file versions and digital objects with, at minimum:
        - repo_id
        - digital_object_id
        - updated_file_uri

    Args:
        updated_file_uri_csv (str): filepath for the csv
        dry_run (bool): run as non-destructive dry run?  True if `--dry-run` provided as an argument
    """
    client = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    csv_dict = read_csv(updated_file_uri_csv)
    for obj in csv_dict:
        repo_id = obj['repo_id']
        digital_object_id = obj['digital_object_id']
        new_uri = obj['updated_file_uri']
        check_uri = obj['check_uri'] or new_uri # In some cases - for example mp3s rendered via a javascript viewer - 
        # we want to check the direct `mads/id/` url and not the `mads/view` player url, as that viewer will always 
        # return 200 even when the asset is missing.
        if check_url(check_uri):
            do = get_digital_object(client, repo_id, digital_object_id)
            if do is not None:
                data = build_digital_object(do, new_uri)
                if not dry_run:
                    update_digital_object(client, repo_id, digital_object_id, data)
                else:
                    message = f"""
Digital object {digital_object_id} would be updated with the following data:
    {data}
"""
                    logger.info(message)
                    print(message)

if __name__ == "__main__":
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for a in args.__dict__:
        logger.info(str(a) + ": " + str(args.__dict__[a]))
        print(str(a) + ": " + str(args.__dict__[a]))

    # Run function
    main(args.csvPath, args.dry_run)
