#!/usr/bin/python3
# This script takes a CSV of archival object URIs as inputs, grabs all the archival objects' JSON data using the API,
# saves them to a jsonL file using the jsonl_path input, and updates the archival objects' update_refid field to
# True, posting them back to ArchivesSpace which regenerates the refids.
import argparse
import os
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, write_to_file

logger.remove()
log_path = Path('../../logs', 'update_refids_{time:YYYY-MM-DD}.log')
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


def main(csv_path, jsonl_path, dry_run=False):
    """
    This script takes a CSV of archival object URIs as inputs, grabs all the archival objects' JSON data using the API,
    saves them to a jsonL file using the jsonl_path input, and updates the archival objects' update_refid field to
    True, posting them back to ArchivesSpace which regenerates the refids.

    The CSV should have the following data structure:
    - Column 1 header = uri
    - Column 1 rows = repositories/##/archival_objects/#######

    Args:
        csv_path (str): filepath of the CSV file with the archival object URIs
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    for uri in read_csv(csv_path):
        uri_parts = uri['uri'].split('/')
        archival_object = local_aspace.get_object('archival_objects', uri_parts[3],
                                                  f'repositories/{uri_parts[1]}')
        write_to_file(jsonl_path, archival_object)
        if archival_object:
            archival_object['caas_regenerate_ref_id'] = True
            if dry_run:
                print(f'Updated archival object {uri['uri']}: {archival_object['caas_regenerate_ref_id']}')
            else:
                post_response = local_aspace.update_object(archival_object['uri'], archival_object)
                if post_response:
                    print(post_response)


# Call with `python update_refids.py <filpath>.csv`
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
