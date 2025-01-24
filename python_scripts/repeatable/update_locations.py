#!/usr/bin/python3
# This script takes a CSV file containing the URIs of locations to be updated and the repository identifier number as
# script arguments, structured like so: `python update_locations.py <filename>.csv <repo_id>`
# The CSV should have at least one of the headers labeled URI. The script adds an
# 'owner repo' = {'ref': 'repository/<repo_numer>'} key-value to the location JSON retrieved from the API, then posts
# the updated JSON to ArchivesSpace
import os
import sys

from copy import deepcopy
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, record_error, write_to_file

logger.remove()
log_path = Path('../logs', 'update_locations_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)


def add_repo(location_data, repository_id):
    """
    Takes a location record and adds a new repository code to it, assigning it to that repository
    Args:
        location_data (dict): the Location JSON data
        repository_id (int): the repository identifier to add to the location

    Returns:
        update_status (str): the status of the POST request
    """
    if type(repository_id) is not int:
        record_error('add_repo() - Unable to add repository code', TypeError)
    else:
        updated_repo = deepcopy(location_data)
        updated_repo['owner_repo'] = {'ref': f'/repositories/{str(repository_id)}'}
        return updated_repo

def main(csv_location, repo_id):
    """
    Takes a CSV of location URIs and repository identifier and adds an owner_repo to the location JSON data

    Args:
        csv_location (str): filepath of the CSV containing the location URIs to update
        repo_id (int): the repository identifier number to add to the location JSON data
    """
    original_location_json = str(Path('../logs', 'update_locations_original_data.jsonl'))
    print(original_location_json)
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    uris = read_csv(str(Path(os.getcwd(), csv_location)))
    for row in uris:
        location_uri = row['uri'].split('/')
        location_type, location_id = location_uri[1], location_uri[2]
        location_data = local_aspace.get_object(location_type, location_id)
        write_to_file(original_location_json, location_data)
        updated_location = add_repo(location_data, repo_id)
        update_status = local_aspace.update_object(row['uri'], updated_location)
        if 'error' in update_status:
            record_error(f'main() - Error updating location {row["uri"]}', update_status)
        else:
            logger.info(update_status)
            print(update_status)

# Call with `python update_locations.py <filename>.csv <repo_id>`
if __name__ == '__main__':
    main(csv_location=str(Path(f'{sys.argv[1]}')), repo_id=int(f'{sys.argv[2]}'))