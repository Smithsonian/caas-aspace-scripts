#!/usr/bin/python3
# This script
import argparse
import os
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(
    os.path.dirname("python_scripts")
)  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, record_error, write_to_file

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)


def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to the CSV file for updating data", type=str)
    parser.add_argument("jsonPath", help="path to the JSONL file for storing data", type=str)
    parser.add_argument("logFolder", help="path to the log folder for storing log files", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action="store_true")
    parser.add_argument("--version", action="version", version="%(prog)s - Version 1.0")

    return parser.parse_args()


def main(instances_csv, jsonl_path, dry_run=False):
    """
    This script

    Args:
        instances_csv (str): filepath of the CSV containing archival object URIs and instance type value to update
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    aspace_api = ASpaceAPI(os.getenv("as_api"), os.getenv("as_un"), os.getenv("as_pw"))
    archival_objects = read_csv(instances_csv)
    for archival_object in archival_objects:
        ao_json = aspace_api.get_object('archival_objects',
                                    int(archival_object['ao_ID']),
                                    '/repositories/20')
        if ao_json:
            write_to_file(jsonl_path, ao_json)
            if 'instances' in ao_json:
                for instance in ao_json['instances']:
                    if 'digital_object' in instance:
                        pass
                    else:
                        instance['instance_type'] = archival_object['updated_instance_value']
                        if dry_run:
                            print(f'{archival_object['ao_refID']}: {instance['instance_type']} > '
                                  f'{archival_object['updated_instance_value']}')
                            logger.info(f'{archival_object['ao_refID']}: {instance['instance_type']} > '
                                        f'{archival_object['updated_instance_value']}')
                        else:
                            post_result = aspace_api.update_object(ao_json['uri'], ao_json)
                            print(post_result)
                            logger.info(post_result)


# Call with `python update_instancetype.py <jsonl_filepath>.jsonl <log_folder_path>`
if __name__ == "__main__":
    args = parseArguments()

    # Set up log file
    logger.remove()
    log_path = Path(args.logFolder, "update_instancetype_{time:YYYY-MM-DD}.log")
    logger.add(str(log_path), format="{time}-{level}: {message}")

    # Print arguments
    logger.info(f"Running {sys.argv[0]} script with following arguments: ")
    print(f"Running {sys.argv[0]} script with following arguments: ")
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(instances_csv=args.csvPath, jsonl_path=args.jsonPath, dry_run=args.dry_run)
