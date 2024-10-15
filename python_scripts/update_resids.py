#!/usr/bin/env python

# This script takes a CSV file of resource identifiers, edits them to standardize them to contain only alphanumeric
# characters, except periods using those as separators, and posts those changes to ArchivesSpace
import csv
import json
import re

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from collections import namedtuple
from loguru import logger
from pathlib import Path
from secrets import *

alphanumeric_capture = re.compile(r'[a-zA-Z0-9.-]*', re.UNICODE)

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
    Takes a csv input of ASpace resource identifiers - ran from SQL query - and returns a list of all
    dictionaries of all the objects metadata, including their identifiers, repository ID, ASpace ID, and URI

    Args:
        all_ids_csv (str): filepath for CSV file

    Returns:
        resources (list): a list of dictionaries for each column name (key) and row values (value)
    """
    try:
        open_csv = open(all_ids_csv, 'r', encoding='UTF-8')
        resources = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return resources


def remove_nonalphanums(identifier_value):
    """
    Takes a string input for a resource identifier value, removes all non-alphanumeric characters except periods and
    returns a new identifier value

    Args:
        identifier_value (str): the identifier value from id_0, id_1, id_2, and id_3 fields in a resource identifier

    Returns:
        updated_id_value (str): the identifier value from id_0, id_1, id_2, and id_3 fields in a resource identifier
        containing only alphanumeric characters except periods
    """
    replaced_characters = re.findall(alphanumeric_capture, identifier_value)
    no_alphanums = "".join(replaced_characters)
    updated_id_value = no_alphanums.replace('-', '.')
    return updated_id_value

def concatenate_idfields(full_identifier):
    """
    Takes a list of the components for a resource identifier and concatenates them into a single string if their value
    is not null

    Args:
        full_identifier (list): contains the values for id_0, id_1, id_2, and id_3 fields for resource identifiers

    Returns:
        concatenated_identifier (str): combined identifier from id_0, id_1, id_2, and id_3 fields for resource
        identifiers
    """
    pass


def check_eadid(updated_identifier, resource_uri, aspace_client):
    """
    Makes an ASpace API call to grab the resource JSON data, compares the updated identifier value to the EAD ID listed,
    and if it matches, returns True. If it does not match, returns False.

    Args:
        updated_identifier (str): the concatenated identifier values from id_0, id_1, id_2, and id_3 fields in a
        resource identifier containing only alphanumeric characters except periods
        resource_uri (str): The URI for the resource record in ArchivesSpace
        aspace_client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API

    Returns:
        match_eadid (bool): if True, EAD ID and updated identifier match. If False, EAD ID and updated identifier do not
        match
    """
    pass


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


def main():
    aspace_client = client_login(as_api, as_un, as_pw)
    resources = read_csv(f'../test_data/resource_accession_IDs_all.csv')
    for resource in resources:
        identifier_values = json.loads(resource['identifier'])
        update_identifiers = []
        for id_field in identifier_values:
            if id_field:
                update_identifiers.append(remove_nonalphanums(id_field))
        print(update_identifiers)




if __name__ == "__main__":
    main()
