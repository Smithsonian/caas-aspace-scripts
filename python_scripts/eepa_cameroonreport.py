#!/usr/bin/env python

# This script takes CSV files listing specific collections from EEPA repository, extracts the resource URIs listed in
# each CSV, uses the ArchivesSpace API to grab the Abstract or Scope and Contents note from the JSON data, and writes
# the note to the provided CSV in a new column
import csv
import json

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from collections import namedtuple
from loguru import logger
from pathlib import Path
from secrets import *

logger.remove()
log_path = Path(f'../logs', 'report_eepacameroon_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")


def client_login(as_api, as_un, as_pw):
    """
    Login to the ArchivesSnake client and return client

    Args:
        as_api (str): ArchivesSpace API URL
        as_un (str): ArchivesSpace username - admin rights preferred
        as_pw (str): ArchivesSpace password

    Returns:
        client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API
    """
    client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)
    try:
        client.authorize()
    except ASnakeAuthError as e:
        print(f'Failed to authorize ASnake client. ERROR: {e}')
        logger.error(f'Failed to authorize ASnake client. ERROR: {e}')
        return ASnakeAuthError
    else:
        logger.info(f'Connected to ASnake client')
        return client


def read_csv(all_ids_csv):
    """
    Takes a csv input of ASpace resources and returns a list of dictionaries of all the objects metadata, including
    their URIs

    Args:
        all_ids_csv (str): filepath for the CSV

    Returns:
        resources (list): a list of dictionaries for each column name (key) and row values (value)
    """
    resources = []
    try:
        open_csv = open(all_ids_csv, 'r', encoding='UTF-8')
        resources = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return resources


def main():
    aspace_client = client_login(as_api, as_un, as_pw)


if __name__ == "__main__":
    main()
