#!/usr/bin/python3
# This script takes a CSV file containing the URIs or URLs of objects to suppress in the ArchivesSpace staff interface,
# unpublishes and sets the finding aid status to staff only (for resources). The CSV should have a header row that reads
# "URI", and you can pass the object's repository identifier number and object type (resources, archival_objects,
# digital_objects) as script arguments. The script takes the CSV, splits the URI into the ArchivesSpace resource ID,
# repository ID (if not already supplied) and object type (if not already supplied), grabs the resource JSON data, then
# passes the data to the update_publish_status function, which modifies the JSON to publish=False and
# finding_aid_status=staff_only (for resources only). Then it posts the updated JSON to ArchivesSpace and suppresses
# the record.
import argparse
import os
import sys

from copy import deepcopy
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, record_error

logger.remove()
log_path = Path('../logs', 'suppress_objects_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to csv input file", type=str)
    parser.add_argument("repoID", help="the ASpace repo id number", type=int)
    parser.add_argument("objectType", help="resources/archival_objects/digital_objects", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()


def update_publish_status(object_json, object_type):
    """

    Args:
        object_json (dict): the JSON data of the object we want to unpublish and set FA status to staff_only if resource
        object_type (str): the object type to update: resources, archival_objects, digital_objects

    Returns:
        updated_json (dict): the JSON data of the resource updated with publish=False and finding_aid_status=staff_only
    """
    acceptable_types = ['resources', 'archival_objects', 'digital_objects']
    if object_type not in acceptable_types:
        record_error(f'update_publish_status() - provided object type is not in {acceptable_types}',
                     ValueError)
    else:
        updated_object = deepcopy(object_json)
        if object_type == "resources":
            updated_object["finding_aid_status"] = 'staff_only'
        updated_object["publish"] = False
        return updated_object


def main(csv_location, repo_id=None, object_type=None, dry_run=False):
    """
    Takes a CSV of object URIs or URLs, searches for them in ArchivesSpace, then unpublishes, suppresses, and sets the
    finding_aid_status if resource to staff_only using the API

    Args:
        csv_location (str): filepath of the CSV containing the location URIs to update
        repo_id (int): repository ID if the CSV does not contain the repository ID within the object URI
        object_type (str): the type of object you want to suppress: resources, archival_objects, digital_objects
        dry_run (bool): if True, do not suppress resources. Just print statements confirming the resources to suppress
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    uris = read_csv(str(Path(os.getcwd(), csv_location)))
    for row in uris:
        object_uri_parts = list(filter(None, row['URL'].split('/')))  # Filter out any empty strings
        try:
            resource_aspace_id = int(object_uri_parts[-1])
        except ValueError:  # If anything other than an integer in the ASpace generated object ID, then throw error
            record_error(f'main() - error getting object ID {object_uri_parts[-1]}', ValueError)
        else:
            if repo_id is None:
                repo_id = object_uri_parts[1]
            if object_type is None:
                object_type = object_uri_parts[2]
            original_object = local_aspace.get_object(object_type,
                                                      resource_aspace_id,
                                                      f'repositories/{repo_id}')
            if original_object:
                updated_object = update_publish_status(original_object, object_type)
                if dry_run is True:
                    print(f'This is what the post will look like: {updated_object}')
                else:
                    update_status = local_aspace.update_object(updated_object['uri'], updated_object)
                    if update_status is not None:
                        print(update_status)
                        logger.info(update_status)
                        suppress_message = local_aspace.update_suppression(updated_object['uri'], True)
                        if suppress_message is not None:
                            print(suppress_message)
                            logger.info(suppress_message)


if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(args.csvPath, args.repoID, args.objectType, args.dry_run)
