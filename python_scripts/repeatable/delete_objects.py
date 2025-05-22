#!/usr/bin/python3
# This script takes a CSV of URIs and object type as inputs, grabs all the locations' JSON data using the API, saves
# them to a jsonL file using the jsonl_path input, and then deletes them in ArchivesSpace. It's recommended to check to
# see if locations have any top containers associated with them. You can run an SQL query to find any associated top
# containers such as the following:
# SELECT * FROM top_container_housed_at_rlshp
# WHERE
# location_id in (49324,49338,49323,etc.)
import argparse
import os
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, write_to_file

logger.remove()
log_path = Path('../../logs', 'delete_locations_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to CSV input file", type=str)
    parser.add_argument("jsonPath", help="path to the JSONL file for storing data", type=str)
    parser.add_argument("objectType", help="resources/archival_objects/digital_objects", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()


def main(csv_path, jsonl_path, objectType, dry_run=False):
    """
    This script takes a CSV of URIs and object type as inputs, grabs all the locations' JSON data using the API, saves
    them to a jsonL file using the jsonl_path input, and then deletes them in ArchivesSpace.

    The CSV should have the following data structure:
    - Column 1 header = uri
    - Column 1 rows = /locations/#######

    Args:
        csv_path (str): filepath of the CSV file with the location URIs
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        objectType (str): the type of object you want to delete. resources/archival_objects/digital_objects/locations
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    for uri in read_csv(csv_path):
        uri_parts = uri['uri'].split('/')
        location = local_aspace.get_object(objectType, uri_parts[2])
        write_to_file(jsonl_path, location)
        if location:
            if dry_run:
                print(f'Deleted location {uri['uri']}')
            else:
                post_response = local_aspace.delete_object(location['uri'])
                if post_response:
                    print(post_response)


# Call with `python delete_objects.py <csv_filpath>.csv <jsonl_filepath>.jsonl <object type>`
if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(csv_path=args.csvPath, jsonl_path= args.jsonPath, objectType=args.objectType, dry_run=args.dry_run)
