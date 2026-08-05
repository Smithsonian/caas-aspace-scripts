#!/usr/bin/python3
# This script takes a CSV file containing the URIs for resource records to get and post back to ArchivesSpace without
# updating any data, used to kickstart an update to EDAN/SOVA by updating the system_mtime field.
import argparse
import os
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from loguru import logger

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, record_error, write_to_file

logger.remove()
log_path = Path('../logs', 'touch_resources_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to csv input file", type=str)
    parser.add_argument("jsonPath", help="path to the JSONL file for storing data", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()


def main(csv_location, jsonl_path, dry_run=False):
    """
    This script takes a CSV file containing the URIs for resource records to get and post back to ArchivesSpace without
    updating any data, used to kickstart an update to EDAN/SOVA by updating the system_mtime field.

    Structure the CSV like so:

    uri
    repositories/##/resources/object_id
    repositories/##/resources/object_id

    Args:
        csv_location (str): filepath of the CSV containing the location URIs to update
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, do not suppress resources. Just print statements confirming the resources to suppress
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    uris = read_csv(str(Path(os.getcwd(), csv_location)))
    for row in uris:
        object_uri_parts = list(filter(None, row['uri'].split('/')))  # Filter out any empty strings
        try:
            resource_aspace_id = int(object_uri_parts[-1])
        except ValueError:  # If anything other than an integer in the ASpace generated object ID, then throw error
            record_error(f'main() - error getting object ID {object_uri_parts[-1]}', ValueError)
        else:
            repo_id = object_uri_parts[1]
            object_type = object_uri_parts[2]
            original_object = local_aspace.get_object(object_type, resource_aspace_id,f'repositories/{repo_id}')
            if original_object:  # if returned JSON is not None
                if dry_run:
                    print(f'This is what the post will look like: {original_object['uri']}')
                else:
                    write_to_file(jsonl_path, original_object)
                    update_status = local_aspace.update_object(original_object['uri'], original_object)
                    if update_status is not None:
                        print(update_status)
                        logger.info(update_status)
            else:
                print(f'main() - Trouble getting resource JSON: {original_object['uri']}')
                logger.error(f'main() - Trouble getting resource JSON: {original_object['uri']}')


if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(args.csvPath, args.jsonPath, args.dry_run)
