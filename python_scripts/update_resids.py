# This script takes a CSV file of resource identifiers, edits them to standardize them to contain only alphanumeric
# characters, except periods using those as separators, and posts those changes to ArchivesSpace
import csv
import re

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from collections import namedtuple
from loguru import logger
from pathlib import Path
from secrets import *


username_capture = re.compile(r'(?<=z-)(.*)(?=-expired)', re.UNICODE)

logger.remove()
log_path = Path(f'../logs', 'update_resids_{time:YYYY-MM-DD}.log')
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
    # aspace = ASpace(baseurl=as_api_stag, username=as_un, password=as_pw)
    client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)
    try:
        client.authorize()
    except ASnakeAuthError as e:
        print(f'Failed to authorize ASnake client. ERROR: {e}')
        logger.error(f'Failed to authorize ASnake client. ERROR: {e}')
        return ASnakeAuthError
    else:
        return client

def read_csv(all_ids_csv):
    """
    Takes a csv input of ASpace resource identifiers - ran from SQL query - and returns a list of all
    dictionaries of all the objects metadata, including their identifiers, repository ID, ASpace ID, and URI

    Args:
        all_ids_csv (str): filepath for the all identifiers csv listing metadata for resources

    Returns:
        resources (list): a list of URIs (dict) with "Missing Title" in their notes
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


def update_resids(aspace_client, updated_resource):
    """
    Takes the updated resource JSON data and posts the new JSON data to ArchivesSpace

    Args:
        aspace_client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API
        updated_resource (dict): the updated resource JSON data with the new identifier

    Returns:
        update_message (dict): ArchivesSpace response

    """
    pass
