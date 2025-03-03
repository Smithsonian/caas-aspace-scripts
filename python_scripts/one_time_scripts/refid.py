#!/usr/bin/env python

# This script updates caas_aspace_refid's based on a provided CSV.  For help on available arguments and options:
# `python repeatable/update_fileuri.py -h`.
import argparse
import os
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path
from python_scripts.utilities import client_login, read_csv

# Logging
logger.remove()
log_path = Path(f'./logs', 'update_refid_{time:YYYY-MM-DD}.log')
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
    
def get_refid(client, resource_uri):
    existing_refid = client.get(f'plugins/caas_next_refid/find_by_uri?resource_uri={resource_uri}').json()
    if 'error' in existing_refid:
        logger.error(f'Refid will be created for {resource_uri}')
        (f'Refid will be created for {resource_uri}')
        return True
    else:
        logger.error(f'Refid already exists for {resource_uri}')
        (f'Refid already exists for {resource_uri}')
    
def build_refid(obj):
    refid = {}
    refid['resource_uri'] = obj['uri']
    refid['next_refid'] = obj['next_refid']

    return refid

def update_refid(client, data):
    resource_uri = data['resource_uri']
    next_refid = data['next_refid']
    update_message = client.post(f'plugins/caas_next_refid/set_by_uri?resource_uri={resource_uri}&next_refid={next_refid}').json()
    if 'error' in update_message:
        logger.error(update_message)
        print(f'ERROR: {update_message}')
    else:
        logger.info(f'{update_message}')
        print(f'Updated object data: {update_message}')

    return update_message

def main(updated_file_uri_csv, dry_run):
    client = client_login(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    csv_dict = read_csv(updated_file_uri_csv)
    for obj in csv_dict:
        resource_uri = obj['uri']
        if get_refid(client, resource_uri):
            data = build_refid(obj)
            if not dry_run:
                update_refid(client, data)
            else:
                message = f"""
Refid {data} would be updated with the following data:
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
