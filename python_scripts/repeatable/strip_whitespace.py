#!/usr/bin/env python

# This script works through a csv of offending content and removes whitespace from the specified field(s).
# For help on available arguments and options:
# `python repeatable/strip_whitespace.py -h`.
import argparse
import os
import sys

from asnake.aspace import ASpace
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path
from python_scripts.utilities import read_csv, record_error

# Logging
logger.remove()
log_name = __file__.rsplit('/',1)[1].replace('.py', '')+'_{time:YYYY-MM-DD}'
log_path = Path(f'./logs/{log_name}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

# Define functions
def archival_objects(repo): return repo.archival_objects
def digital_objects(repo): return repo.digital_objects
def resources(repo): return repo.resources

# Create a dictionary to map arguments to functions
func_dict = {
    "archival_objects": archival_objects,
    "digital_objects": digital_objects,
    "resources": resources
}

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to csv input file", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("-t", "--type", help="type of ArchivesSpace object", choices=func_dict.keys(), required='true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def strip_whitespace(json_object, field_1, field_2):
    """
    Will strip whitespace from a single field when supplied with an ArchivesSpace json object and
    the field to update.  If the targeted field is nested, may supply the parent field in field_1
    and field to act upon in field_2.

    Args:
        json_object (dict): json object from ArchivesSpace
        field_1 (str): the key of the field to strip whitespace from, or, if the targeted field is a
        nested field, the parent of the target field
        field_2 (str): the key of the nested field to strip whitespace from. Will be blank if the
        targeted field is not nested in a subrecord.
    """
    updated_object = {}
    if field_1 in json_object:
        object_1 = json_object[field_1]
        if field_2:
            for i, item in list(enumerate(object_1)):
                json_object[field_1][i][field_2] = item[field_2].strip()
                updated_object = json_object
                return updated_object
        else:
            json_object[field_1] = object_1.strip()
            updated_object = json_object
            return updated_object
    else:
        record_error(f'Field `{field_1}` does not exist in JSON data: ',
                     json_object)

def main(whitespace_csv, dry_run):
    """
    Runs the functions of the script, fetching, digging into, and stripping whitespace from a
    specified record type and field, printing error messages if they occur.

    Takes a csv input of existing ASpace records with, at minimum:
        - id - The id of the record to be updated (ex: a resource id or digital object id).
        - field_1 - The name of the field with offending whitespace.  This is the field name as represented
        in the JSON returned from ArchivesSpace (ex: 'title').  If the field is nested deeper in the record,
        this will be the name of the parent (for example, if wishing to strip whitespace from a digital 
        object's nested file_uri, field_1 would be 'file_versions').
        - field_2 - For nested fields, the name of the field with offending whitespace.  This is the field name
        as represented in the JSON returned from ArchivesSpace (ex: 'file_uri').  This will be blank if the
        field in field_1 is the field targeted for update.
        - repo_id - The repo_id of the record to be updated

    Args:
        whitespace_csv (str): filepath for the csv
        dry_run (bool): run as non-destructive dry run?  True if `--dry-run` provided as an argument
    """

    aspace = ASpace(
        baseurl=os.getenv('as_api'),
        username=os.getenv('as_un'),
        password=os.getenv('as_pw')
    )
    csv_dict = read_csv(whitespace_csv)
    for obj in csv_dict:
        repo = aspace.repositories(obj['repo_id'])
        existing_object = func_dict[args.type](repo)(obj['id'])
        if isinstance(existing_object, dict) and 'error' in existing_object:
            record_error(f'Unable to retrieve object with provided URI: '
                         f'repositories/{obj["repo_id"]}/{args.type}/{obj["id"]}',
                         existing_object)
            return None
        elif existing_object is not None:
            json_object = existing_object.json()
            data = strip_whitespace(json_object, obj['field_1'], obj['field_2'])
            if not dry_run:
                update_message = aspace.client.post(data['uri'], json=data).json()
                if 'error' in update_message:
                    record_error('update_object() - Update failed due to following error', update_message)
                    return None
                else:
                    logger.info(f'{update_message}')
                    print(f'Updated object data: {update_message}')
            else:
                message = f"""
{args.type} {obj['id']} would be updated with the following data:
{data}
"""
                logger.info(message)
                print(message)
            
if __name__ == "__main__":
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for a in args.__dict__:
        logger.info(str(a) + ": " + str(args.__dict__[a]))
        print(str(a) + ": " + str(args.__dict__[a]))

    # Run function
    main(args.csvPath, args.dry_run)
