#!/usr/bin/python3
# This script takes a CSV of URIs and object type as inputs, grabs all the objects' JSON data using the API, saves
# them to a jsonL file using the jsonl_path input, and then deletes them in ArchivesSpace. Structure the CSV like so:
# uri
# /repositories/##/object_type/object_id
import argparse
import os
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, write_to_file, record_error

logger.remove()
log_path = Path('../../logs', 'delete_objects_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to CSV input file", type=str)
    parser.add_argument("jsonPath", help="path to the JSONL file for storing data", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def retrieve_object_json(object_uri, local_aspace):
    """
    Splits the given URI for the object via / and retrieves the object's JSON.
    Args:
        object_uri (DictReader object): the URI of the object
        local_aspace (ASpaceAPI object): an instance of the ASpace API for connecting to the client

    Returns:
        object_json (dict): the JSON metadata for the object URI
    """
    try:
        uri_parts = object_uri['uri'].split('/')
        object_type, object_id = uri_parts[-2], uri_parts[-1]
    except IndexError as spliterror:
        record_error('retrieve_object_json() - Failed to split URI', spliterror)
        return None
    else:
        if "repositories" in uri_parts:
            repo_uri = f'repositories/{uri_parts[2]}'
            object_json = local_aspace.get_object(object_type, object_id, repo_uri)
        else:
            object_json = local_aspace.get_object(object_type, object_id)
        return object_json


def main(csv_path, jsonl_path, dry_run=False):
    """
    This script takes a CSV of URIs and object type as inputs, grabs all the objects' JSON data using the API, saves
    them to a jsonL file using the jsonl_path input, and then deletes them in ArchivesSpace.

    The CSV should have the following data structure:
    - Column 1 header = uri
    - Column 1 rows = /locations/#######

    Args:
        csv_path (str): filepath of the CSV file with the object URIs
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    for uri in read_csv(csv_path):
        object_json = retrieve_object_json(uri, local_aspace)
        write_to_file(jsonl_path, object_json)
        if object_json:
            if dry_run:
                print(f'Object would be deleted: {uri['uri']}')
            else:
                post_response = local_aspace.delete_object(object_json['uri'])
                if post_response:
                    print(post_response)


# Call with `python delete_objects.py <csv_filpath>.csv <jsonl_filepath>.jsonl`
if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(csv_path=args.csvPath, jsonl_path= args.jsonPath, dry_run=args.dry_run)
