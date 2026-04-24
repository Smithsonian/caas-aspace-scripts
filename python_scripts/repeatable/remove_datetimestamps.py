#!/usr/bin/python3
# This script takes a CSV of archival object URIs with timestamps in their date begin and/or end fields, retrieves the
# objects using the ASpace API, removes the timestamps, and re-posts the archival objects to ASpace.
import argparse
import os
import sys

from copy import deepcopy
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, write_to_file

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)


def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to CSV input file", type=str)
    parser.add_argument("jsonPath", help="path to the JSONL file for storing data", type=str)
    parser.add_argument("logFolder", help="path to the log folder for storing log files", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()


def update_date(date):
    """
    Takes a date field (begin or end) from the archival object JSON data, strips any leading/trailing spaces, and
    removes any timestamps, returning the updated date. Warns user if the updated date is longer than 10 characters,
    which indicates an improperly formatted date.

    Args:
        date(str): the date as listed in the archival object JSON data, from either the begin or end fields.

    Returns:
        updated_date(str): an updated copy of the input date with leading spaces and timestamp removed.
    """
    updated_date = deepcopy(date)
    updated_date = updated_date.strip()
    if 'T' in updated_date:
        updated_date = updated_date.split('T')[0]
    if len(updated_date) > 10:
        print(f'The following date is longer than 10 characters: {updated_date}')
        logger.warning(f'The following date is longer than 10 characters: {updated_date}')
    return updated_date


def main(csvPath, jsonl_path, dry_run=False):
    """
    This script takes a CSV of archival object URIs with timestamps in their date begin and/or end fields, retrieves the
    objects using the ASpace API, removes the timestamps, and re-posts the archival objects to ASpace.

    The CSV should have the following columns:
    - uri, ex: repositories/27/archival_objects/3938698

    Args:
        csvPath (str): filepath of the CSV file containing all EAD IDs to suppress in EDAN
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the prepared EDAN post but does not post to EDAN
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    for date_row in read_csv(csvPath):
        object_uri_parts = list(filter(None, date_row['uri'].split('/')))  # Filter out any empty strings
        ao_json = local_aspace.get_object(object_uri_parts[2], object_uri_parts[3],
                                          f'repositories/{object_uri_parts[1]}')
        write_to_file(jsonl_path, ao_json)
        for date in ao_json['dates']:
            date_index = 0
            if 'begin' in date:
                ao_json['dates'][date_index]['begin'] = update_date(ao_json['dates'][date_index]['begin'])
            if 'end' in date:
                ao_json['dates'][date_index]['end'] = update_date(ao_json['dates'][date_index]['end'])
            date_index += 1
        if dry_run:
            print(f'The following date(s) would be updated for archival object {date_row['uri']}: {ao_json['dates']}')
            logger.info(f'The following date(s) would be updated for archival object {date_row['uri']}: '
                        f'{ao_json['dates']}')
        else:
            response = local_aspace.update_object(date_row['uri'], ao_json)
            print(f'The following archival object date(s) have been updated: {date_row['uri']}, {response}')
            logger.info(f'The following archival object date(s) have been updated: {date_row['uri']}, {response}')


# Call with `python remove_datetimestamps.py <input_filename>.csv <jsonl_filepath>.jsonl <logfile_path>.log`
if __name__ == '__main__':
    args = parseArguments()

    # Set up log file
    logger.remove()
    log_path = Path(args.logFolder, 'remove_datetimestamps_{time:YYYY-MM-DDTHH-MM-SS}.log')
    logger.add(str(log_path), format="{time}-{level}: {message}")

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(csvPath=args.csvPath, jsonl_path=args.jsonPath, dry_run=args.dry_run)
