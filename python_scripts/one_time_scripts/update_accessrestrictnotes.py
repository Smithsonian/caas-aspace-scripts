#!/usr/bin/python3
# This script takes a CSV containing resource info (Id, resource_uri, updated_access_note) and retrieves the JSON
# data for any resources whose rows in the CSV contain data in the updated_access_note column. Then, it makes a copy
# of the resource JSON, updating the accessrestrict note's content with the data found in the updated_access_note
# cell. Finally, it posts the updated JSON to ArchivesSpace.
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

    parser.add_argument("csvPath",
                        help="the filepath to the CSV of updated accessrestrict notes", type=str)
    parser.add_argument("jsonPath",
                        help="path to the JSONL file for storing original accessrestrict data", type=str)
    parser.add_argument("logFolder", help="path to the log folder for storing log files", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()


def main(accessrestrict_csv, backup_jsonl, dry_run=False):
    """
    This script takes a CSV containing resource info (Id, resource_uri, updated_access_note) and retrieves the JSON
    data for any resources whose rows in the CSV contain data in the updated_access_note column. Then, it makes a copy
    of the resource JSON, updating the accessrestrict note's content with the data found in the updated_access_note
    cell. Finally, it posts the updated JSON to ArchivesSpace.

    Args:

        accessrestrict_csv (str): filepath of the CSV containing updates to accessrestrict notes and resource info
        backup_jsonl (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    resources = read_csv(accessrestrict_csv, encoding_type='UTF-8-SIG')
    for resource in resources:
        if resource['updated_access_note']:
            accessrestrict_count = 0
            uri_components = resource['resource_uri'].split('/')
            original_resource_data = local_aspace.get_object(uri_components[3], uri_components[4], f'{uri_components[1]}/{uri_components[2]}')
            write_to_file(backup_jsonl, original_resource_data)
            updated_resource = deepcopy(original_resource_data)
            for note in updated_resource['notes']:
                if 'type' in note:
                    if note['type'] == 'accessrestrict':
                        if accessrestrict_count == 0:
                            if len(note['subnotes']) > 1:
                                logger.warning(f'There are more than 1 subnotes to this accessrestrict note. Only the '
                                               f'first subnote will be updated.\n{note["subnotes"]}')
                            old_accessrestrict = note['subnotes'][0]['content']
                            note['subnotes'][0]['content'] = resource['updated_access_note']
                            if dry_run:
                                logger.info(f'{resource["Id"]}\n'
                                            f'Old accessrestrict note: {old_accessrestrict}\n'
                                            f'Updated accessrestrict note: {resource["updated_access_note"]}')
                                print(f'{resource["Id"]}\n'
                                      f'Old accessrestrict note: {old_accessrestrict}\n'
                                      f'Updated accessrestrict note: {resource["updated_access_note"]}\n\n')
                            else:
                                update_message = local_aspace.update_object(resource['resource_uri'], updated_resource)
                                logger.info(f'main() - Updated {resource["Id"]}: {update_message}')
                                print(f'main() - Updated {resource["Id"]}: {update_message}')
                            accessrestrict_count += 1
                        else:
                            logger.info(f'main() - More than 1 accessrestrict note exists, only updating the first. '
                                        f'Additional accessrestrict notes: {note}')



# Call with `python update_accessrestrictnotes.py <csvPath>.csv <jsonl_filepath>.jsonl <log_folder_path>`
if __name__ == '__main__':
    args = parseArguments()

    # Set up log file
    logger.remove()
    log_path = Path(args.logFolder, 'update_accessrestrictnotes_{time:YYYY-MM-DD}.log')
    logger.add(str(log_path), format="{time}-{level}: {message}")

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(accessrestrict_csv=args.csvPath, backup_jsonl=args.jsonPath, dry_run=args.dry_run)