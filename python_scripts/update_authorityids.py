#!/usr/bin/env python

# This script intakes a CSV of all subjects and agends in ArchivesSpace to update their Authority IDs to match the
# following standard: <https://<authority_url>/<authority_id>>
import copy
import csv

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from collections import namedtuple
from itertools import islice
from loguru import logger
from pathlib import Path
from secrets import *


logger.remove()
log_path = Path(f'../logs', 'update_authorityids_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")


class ArchivesSpace:
    def __init__(self, repo_id):
        self.repository_uri = f'/repositories/{repo_id}/'
        try:
            self.aspace_client = ASnakeClient(baseurl=as_api_stag, username=as_un, password=as_pw)  # TODO: replace as_api_stag with as_api_prod
        except ASnakeAuthError as e:
            print(f'Failed to authorize ASnake client. ERROR: {e}')
            logger.error(f'Failed to authorize ASnake client. ERROR: {e}')
            raise ASnakeAuthError

    def get_object_metadata(self, object_identifier, object_type):
        """
        Take the object's URI and return the full JSON metadata for the object

        Args:
            object_identifier (int): the object's ArchivesSpace identifier
            object_type (str): the type of the object, either 'accession' or 'resource'

        Returns:
             object_json (dict): the given object's JSON metadata
        """

        if object_type == 'accession':
            object_json = self.aspace_client.get(f'{self.repository_uri}/accessions/{object_identifier}').json()
        elif object_type == 'resource':
            object_json = self.aspace_client.get(f'{self.repository_uri}/resources/{object_identifier}').json()
        else:
            logger.error(f'Provided object is not a resource or accession: {object_identifier} - {object_type}')
            raise TypeError
        return object_json

    def update_identifier(self, object_uri, updated_json):
        """

        Args:
            object_uri (str): the original object's URI for posting to the client
            updated_json (dict): the updated metadata for the object

        Returns:
            update_message (dict): ArchivesSpace response
        """
        update_message = self.aspace.client.post(f'{object_uri}', json=updated_json).json()
        return update_message


def read_csv(authorityids_csv):
    """
    Takes a csv input of ASpace objects with "Missing Title" in them - ran from SQL query - and returns a list of all
    the URIs for those objects

    Args:
        authorityids_csv (str): filepath for the authority IDs csv listing all the URIs for subject and agents to be
    updated

    Returns:
        authorityids_uris (list): a list of dictionaries for each column name (key) and row values (value)
    """
    authorityids_uris = []
    try:
        open_csv = open(authorityids_csv, 'r', encoding='UTF-8')
        authorityids_uris = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return authorityids_uris


def update_authorityids(sbjagt_metadata, test=""):
    """
    Iterate through a subject or agent metdata, update the Authority ID, and return new subject or agent metadata

    Args:
        sbjagt_metadata (dict): subject or agent metadata
        test (str): if using unittests to record in log file, indicate with string input, default is empty string

    Returns:
        new_obj (tuple): returns ERROR, PASS, or UPDATED, then the message or new subject/agent metadata
    """
    Update = namedtuple('Update', 'Status Message')
    new_sbjagt = copy.deepcopy(sbjagt_metadata)


def run_script(accres_ids_csv):
    """
    Runs the functions of the script, taking a csv input containing all the URIs of subjects and agents to update,
    getting the metadata for each and updating their Authority IDs to match the following standard:
    <https://<authority_url>/<authority_id>>, then updated the subjects/agents by posting to ASpace

    Args:
        accres_ids_csv (str): filepath for the accession and resource IDs csv listing all the URIs, IDs, and EADIDs for
        accessions and resources in every repository
    """
    repos = {}
    identifiers = read_csv(accres_ids_csv)
    # for identifier in islice(identifiers, 10):
    #     if identifier["repo_id"] not in repos:
    #         repos[identifier["repo_id"]] = ArchivesSpace(identifier["repo_id"])
    repos = {identifier["repo_id"]: ArchivesSpace(identifier["repo_id"])
             for identifier in identifiers if identifier["repo_id"] not in repos}
    for identifier in identifiers:
        object_metadata = repos[identifier["repo_id"]].get_object_metadata(identifier["uri"])
    print(len(repos))
    print(repos)

    #     aspace_instance = ArchivesSpace()
    # subjectagent_uris = read_csv(authorityids_csv)
    # for uri in subjectagent_uris:
    #     pass


if __name__ == "__main__":
    pass
    run_script(str(Path(f'../test_data/resource_accession_IDs_all.csv')))

