#!/usr/bin/python3
# This script retrieves location IDs with a given building name passed in the oB (originalBuilding) argument using an SQL
# query to the ASpace database. Then it takes a list of those IDs and retrieves their JSON data from the API and
# updates the building field with the argument passed in the uB (updatedBuilding) argument. Then it posts the updated
# location JSON data to ArchivesSpace, saving the original JSON data in a given .jsonl file and logging the results of
# the update to a given log file.
# NOTE: put "" around the building name if it contains spaces, like so: -uB="NMAH-FSD, Building 92"
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

    parser.add_argument("-oB", "--originalBuilding", help="the original building name to search for",
                        type=str)
    parser.add_argument("-uB", "--updatedBuilding", help="the updated building name", type=str)
    parser.add_argument("jsonPath", help="path to the JSONL file for storing original location data",
                        type=str)
    parser.add_argument("logFolder", help="path to the log folder for storing log files", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def location_ids(original_building_name, aspace_db_connection):
    """
    Performs an SQL search for a building name and returns the location IDs of all that match.

    Args:
        original_building_name (str): the text of the building name to search for in the location table
        aspace_db_connection (ASpaceDatabase instance): connection instance to the ASpace database

    Returns:
        matching_ids (list): all the matching location IDs
    """
    find_building = ('SELECT location.id FROM location '
                     'WHERE '
                        f'location.building = "{original_building_name}"')
    sql_results = aspace_db_connection.query_database(find_building)
    formatted_results = [result[0] for result in sql_results]
    return formatted_results

def update_building_name(location_json, updated_name):
    """
    Takes a location JSON record and replaces the building value with the provided updated_name.

    Args:
        location_json (dict): the JSON data for the location object
        updated_name (str): the building name to update

    Returns:
        updated_location (dict): the updated JSON data without leading zeros if present in coordinate indicators
    """
    updated_location = deepcopy(location_json)
    if 'building' in updated_location:
        updated_location['building'] = updated_name
    else:
        logger.error(f'update_building_name() - Error finding key "building" in location JSON for {location_json}')
        print(f'update_building_name() - Error finding key "building" in location JSON for {location_json}')
        return None
    return updated_location


def main(original_building, updated_building, jsonl_path, dry_run=False):
    """
    This script retrieves location IDs with a given building name passed in the oB (originalBuilding) argument using an SQL
    query to the ASpace database. Then it takes a list of those IDs and retrieves their JSON data from the API and
    updates the building field with the argument passed in the uB (updatedBuilding) argument. Then it posts the updated
    location JSON data to ArchivesSpace, saving the original JSON data in a given .jsonl file and logging the results of
    the update to a given log file.

    NOTE: put "" around the building name if it contains spaces, like so: -uB="NMAH-FSD, Building 92"

    Args:
        original_building (str): the text of the building name to search for in the Locations table
        updated_building (str): the updated text of the building name for matching Locations
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    as_database = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                 os.getenv('db_port'))
    matching_ids = location_ids(original_building, as_database)
    for location_id in matching_ids:
        location_json = local_aspace.get_object('locations', location_id)
        write_to_file(jsonl_path, location_json)
        updated_location = update_building_name(location_json, updated_building)
        if dry_run:
            print(f'This is the updated location: {updated_location}')
        else:
            update_result = local_aspace.update_object(updated_location['uri'], updated_location)
            print(update_result)
            logger.info(update_result)


# Call with `python update_locationbuilding.py ob=<original_building_name> uB=<updated_building_name> <jsonl_filepath>.jsonl <log_folder_path>`
if __name__ == '__main__':
    args = parseArguments()

    # Set up log file
    logger.remove()
    log_path = Path(args.logFolder, 'update_locationbuilding_{time:YYYY-MM-DD}.log')
    logger.add(str(log_path), format="{time}-{level}: {message}")

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(original_building=args.originalBuilding, updated_building=args.updatedBuilding, jsonl_path=args.jsonPath,
         dry_run=args.dry_run)