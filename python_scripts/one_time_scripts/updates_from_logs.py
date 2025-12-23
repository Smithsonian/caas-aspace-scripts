#!/usr/bin/env python

import argparse
import json
import os
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path
from python_scripts.utilities import client_login, read_csv

# Logging
logger.remove()
log_name = __file__.rsplit('/',1)[1].replace('.py', '')+'_{time:YYYY-MM-DD}'
log_path = Path(f'./logs/{log_name}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to csv input file", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def post_object(client, path, data):
    """
    Args:
        client (ASnake.client object): client object from ASnake.client
        path (str): post path
        payload (dict): Json payload
    
    Returns:
        update_message (dict): ArchivesSpace API response
    """
    update_message = client.post(path, json=data).json()
    if 'error' in update_message:
        logger.error(update_message)
        print(f'ERROR: {update_message}')
    else:
        logger.info(f'{update_message}')
        print(f'Updated object data: {update_message}')

    return update_message

def main(log_file_csv, dry_run):
    """
    Runs the functions of the script.

    Takes a csv input of valid ASpace post paths and json payloads as such:
        - Path
        - JSON

    Args:
        log_file_csv (str): filepath for the csv
        dry_run (bool): run as non-destructive dry run?  True if `--dry-run` provided as an argument
    """
    client = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    csv_dict = read_csv(log_file_csv)
    for obj in csv_dict:
        path = obj['Path']
        payload = obj['JSON']
        data = json.loads(payload)

        if not dry_run:
            post_object(client, path, data)
        else:
            message = f"""
Object {path} would be updated with the following data:
    {payload}
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
