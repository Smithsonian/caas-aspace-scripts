#!/usr/bin/python3
# This script finds locations with the label "MapCase" and looks for those that have leading zeros in their indicators
# such as 01, 02, etc. It then removes the leading zeros for coordinate_1_indicators and searches for and removes
# leading zeros from coordinate_2_indicators as well. It then posts the updates to those specific locations to ASpace.
# An SQL query is uses to find the appropriate locations.
import argparse
import os
import sys

from copy import deepcopy
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, ASpaceDatabase, write_to_file

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("jsonPath", help="path to the JSONL file for storing data", type=str)
    parser.add_argument("logFolder", help="path to the log folder for storing log files", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def strip_coordinate_leadzero(location_json):
    """
    Searches for a leading zero in a coordinate indicator and removes it if present. Returns the updated JSON data.

    Args:
        location_json (dict): the JSON data for the location object

    Returns:
        updated_location (dict): the updated JSON data without leading zeros if present in coordinate indicators
    """
    updated_location = deepcopy(location_json)
    if 'coordinate_1_indicator' in updated_location:
        if updated_location['coordinate_1_indicator'].startswith('0'):
            updated_location['coordinate_1_indicator'] = updated_location['coordinate_1_indicator'].lstrip('0')
    if 'coordinate_2_indicator' in updated_location:
        if updated_location['coordinate_2_indicator'].startswith('0'):
            updated_location['coordinate_2_indicator'] = updated_location['coordinate_2_indicator'].lstrip('0')
    return updated_location


def main(jsonl_path, dry_run=False):
    """
    This script finds locations with the label "MapCase" and looks for those that have leading zeros in their indicators
    such as 01, 02, etc. It then removes the leading zeros for coordinate_1_indicators and searches for and removes
    leading zeros from coordinate_2_indicators as well. It then posts the updates to those specific locations to ASpace.
    An SQL query is uses to find the appropriate locations.

    Args:
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    as_database = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                 os.getenv('db_port'))
    find_mapcases = ('SELECT location.id FROM location '
                     'WHERE '
                        'coordinate_1_label = "MapCase" '
                     'AND '
                        'building = "NMAH" '
                     'AND '
                        'coordinate_1_indicator LIKE "0_" '
                     'ORDER BY coordinate_1_indicator')
    sql_results = as_database.query_database(find_mapcases)
    for result in sql_results:
        location_json = local_aspace.get_object('locations', result[0])
        write_to_file(jsonl_path, location_json)
        updated_location = strip_coordinate_leadzero(location_json)
        if dry_run:
            print(f'This is the updated container: {updated_location}')
        else:
            update_result = local_aspace.update_object(updated_location['uri'], updated_location)
            print(update_result)
            logger.info(update_result)


# Call with `python update_coordinates.py <jsonl_filepath>.jsonl <log_folder_path>`
if __name__ == '__main__':
    args = parseArguments()

    # Set up log file
    logger.remove()
    log_path = Path(args.logFolder, 'update_coordinates_{time:YYYY-MM-DD}.log')
    logger.add(str(log_path), format="{time}-{level}: {message}")

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(jsonl_path= args.jsonPath, dry_run=args.dry_run)