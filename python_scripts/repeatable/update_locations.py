#!/usr/bin/python3
# This script takes a CSV file containing the URIs of locations to be updated - with at least one of the headers labeled
# URI - and adds a 'owner repo' = {'ref': 'repository/<repo_numer>'} key-value to the location JSON retrieved from the
# API, then posts the updated JSON to ArchivesSpace
import os

from copy import deepcopy
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path
from python_scripts.utilities import read_csv, record_error, write_to_file, ASpaceAPI

logger.remove()
log_path = Path('../logs', 'update_locations_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")


def add_repo(location_data, repository_code):
    """
    Takes a location record and adds a new repository code to it, assigning it to that repository
    Args:
        location_data (dict): the Location JSON data
        repository_code (int): the repository code to add to the location

    Returns:
        update_status (str): the status of the POST request
    """
    if type(repository_code) is not int:
        record_error('add_repo() - Unable to add repository code', TypeError)
    else:
        updated_repo = deepcopy(location_data)
        updated_repo['owner_repo'] = {'ref': f'/repositories/{str(repository_code)}'}
        return updated_repo

def main():
    original_location_json = str(Path('../../test_data', 'update_locations_original_data.jsonl'))
    env_file = find_dotenv(f'.env.prod')
    load_dotenv(env_file)
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    uris = read_csv(str(Path(os.getcwd(), "../../test_data/ACMA_PROD_Locations_URIs-13-01-25.csv")))
    for row in uris:
        location_uri = row['uri'].split('/')
        location_type, location_id = location_uri[1], location_uri[2]
        location_data = local_aspace.get_object(location_type, location_id)
        write_to_file(original_location_json, location_data)
        updated_location = add_repo(location_data, 24)
        update_status = local_aspace.update_object(row['uri'], updated_location)
        if 'error' in update_status:
            record_error(f'main() - Error updating location {row["uri"]}', update_status)
        else:
            logger.info(update_status)
            print(update_status)


if __name__ == '__main__':
    main()