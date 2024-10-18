#!/usr/bin/env python

# This script takes CSV files listing specific collections from EEPA repository, extracts the resource URIs listed in
# each CSV, uses the ArchivesSpace API to grab the Abstract or Scope and Contents note from the JSON data, and writes
# the note to the provided CSV in a new column
import csv

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
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


def read_csv(cameroon_reports_csv):
    """
    Takes a csv input of ASpace resources and returns a list of dictionaries of all the objects metadata, including
    their URIs

    Args:
        cameroon_reports_csv (str): filepath for the CSV

    Returns:
        resources (list): a list of dictionaries for each column name (key) and row values (value)
    """
    resources = []
    try:
        open_csv = open(cameroon_reports_csv, 'r', encoding='UTF-8')
        resources = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return resources


def write_csv(original_filepath, new_filepath, add_values):
    """
    Takes a CSV input and writes a header and values to an additional column at the end of the CSV

    Args:
        original_filepath (str): the filepath of the CSV being read from
        new_filepath (str): the filepath of the new CSV file being written to
        add_values (list): the list of all the new column values to write to in the new CSV

    Returns:

    """
    try:
        with open(original_filepath, 'r', newline='', encoding='utf-8') as readcsv:
            with open(new_filepath, 'w', newline='', encoding='utf-8') as writecsv:
                csvreader = csv.reader(readcsv)
                csvwriter = csv.writer(writecsv)
                row_count = 0
                for row in csvreader:
                    row.append(add_values[row_count])
                    row_count += 1
                    csvwriter.writerow(row)
                writecsv.close()
            readcsv.close()
    except Exception as csverror:
        print(f'Error when reading/writing to CSV: {csverror}')
        logger.error(f'Error when reading/writing to CSV: {csverror}')


def get_resource_metadata(resource_uri, aspace_client):
    """
    Takes an ArchivesSpace resource URI and grabs the JSON metadata using the API

    Args:
        resource_uri (str): the URI for a resource record in ArchivesSpace
        aspace_client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API

    Returns:
        resource_json (dict): the JSON data for an ArchivesSpace resource record
    """
    resource_json = aspace_client.get(resource_uri).json()
    if 'error' in resource_json:
        logger.error(f'ERROR getting object metadata: {resource_json}')
        print(f'ERROR getting object metadata: {resource_json}')
    else:
        return resource_json


def find_abstract_scope(resource_json):
    """
    Takes a JSON string of a resource's metadata and searches it for an Abstract or Scope and Contents note. If either
    is found, return as string (Abstract is preferred if both are present).

    Args:
        resource_json (dict): the JSON data for an ArchivesSpace resource record

    Returns:
        abstract_scope_content (str): the content of an Abstract or Scope and Contents note. If neither are present,
        return an empty string
    """
    abstract_content = ''
    scope_content = ''
    if 'notes' in resource_json:
        if bool(resource_json['notes']) is True:
            for note in resource_json['notes']:
                if 'type' in note:
                    if note['type'] == 'abstract':
                        abstract_content = note['content']
                        if type(abstract_content) is list:
                            all_abstract_contents = [subnote for subnote in note['content']]
                            combined_abstract = " "
                            abstract_content = combined_abstract.join(all_abstract_contents)
                    if note['type'] == 'scopecontent':
                        all_scope_contents = [subnote['content'] for subnote in note['subnotes']
                                              if 'content' in subnote]
                        combined_scope = " "
                        scope_content = combined_scope.join(all_scope_contents)
    if not abstract_content and scope_content:
        return scope_content
    else:
        return abstract_content


def main():
    aspace_client = client_login(as_api_stag, as_un, as_pw)  # TODO: replace as_api_stag with as_api_prod
    reportspath = Path(f'../test_data/EEPA_Cameroon_Reports').glob('*.csv')
    for file in reportspath:
        abstractscope_column_values = ['Abstract/Scope']
        new_report_filepath = str(file)[:-4] + '-Abstracts.csv'
        report_collections = read_csv(str(file))
        for collection in report_collections:
            print(collection['uri'])
            resource_json = get_resource_metadata(collection['uri'], aspace_client)
            abstractscope_column_values.append(find_abstract_scope(resource_json))
        write_csv(file, new_report_filepath, abstractscope_column_values)


if __name__ == "__main__":
    main()
