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
from http.client import HTTPException
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, ASpaceDatabase, record_error, write_to_file

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("-oB", "--originalBuilding", help="the original building name to search for",
                        type=str)
    parser.add_argument("-uB", "--updatedBuilding", help="the updated building name", type=str)
    parser.add_argument("-mR", "--moveRoomFloor", help="move Room value to Floor if True", type=bool)
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

def update_building_name(location_ids, update_name, aspace_connection):
    """
    Takes a location JSON record and replaces the building value with the provided updated_name.

    Args:
        location_ids (list): the IDs for all the locations to update
        update_name (str): the building name to update on the given location IDs
        aspace_connection (ASpaceAPI Instance): an instance of the ASpaceAPI class from utilities.py

    Returns:
        update_response (list): the response from the POST request
    """
    try:
        post_message = aspace_connection.aspace_client.post('locations/batch_update',
                                                            json={"record_uris": location_ids,
                                                                  "building": update_name}).json()
    except HTTPException as get_error:
        record_error(f'update_building_name() - Unable to make post request with record_uris: {location_ids}; '
                     f'building: {update_name}', get_error)
    else:
        if 'error' in post_message:
            record_error(f'get_object() - Unable to retrieve object in: '
                         f'{location_ids}',
                         post_message)
        else:
            return post_message

def move_room_to_floor(location_json):
    """
    Takes a location JSON record and replaces the floor value with the room value and deletes the room value from
    the room field.

    Args:
        location_json (dict): the JSON data for the location object

    Returns:
        updated_location (dict): the updated JSON data with the updated floor and room values
    """
    updated_location = deepcopy(location_json)
    if 'room' in updated_location and 'floor' in updated_location:
        if updated_location['room']:
            updated_location['floor'] = updated_location['room']
            updated_location['room'] = ''
            return updated_location
        else:
            record_error(f'move_room_to_floor() - No value in Room field to move to Floor field for {location_json}', ValueError)
            return None
    elif 'room' in updated_location and 'floor' not in updated_location:
        updated_location['floor'] = updated_location['room']
        updated_location['room'] = ''
        return updated_location
    else:
        record_error(f'move_room_to_floor() - Room field not found in {location_json}', ValueError)
        return None



def main(original_building, jsonl_path, updated_building=None, move_floor=False, dry_run=False):
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
        move_floor (bool): if True, move the value in Room to the Floor field and remove Room value from Room field
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    as_database = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                 os.getenv('db_port'))
    matching_ids = location_ids(original_building, as_database)
    location_uris = []
    for location_id in matching_ids:
        location_json = local_aspace.get_object('locations', location_id)
        write_to_file(jsonl_path, location_json)
        location_uris.append(f'/locations/{location_id}')
        if move_floor:
            updated_location = move_room_to_floor(location_json)
            if dry_run:
                print(f'This is the updated location: {updated_location}')
            else:
                if updated_location:
                    update_result = local_aspace.update_object(updated_location['uri'], updated_location)
                    print(update_result)
                    logger.info(update_result)
    if updated_building:
        updated_location = update_building_name(location_uris[:10], updated_building, local_aspace)
        if dry_run:
            print(f'This is the updated location: {updated_location}')
        else:
            if updated_location:
                update_result = local_aspace.update_object(updated_location['uri'], updated_location)
                print(update_result)
                logger.info(update_result)


# Call with `python update_locationbuilding.py -ob=<original_building_name> -uB=<updated_building_name> -mR=<True_or_False> <jsonl_filepath>.jsonl <log_folder_path>`
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
    main(original_building=args.originalBuilding, jsonl_path=args.jsonPath, updated_building=args.updatedBuilding,
         move_floor=args.moveRoomFloor, dry_run=args.dry_run)