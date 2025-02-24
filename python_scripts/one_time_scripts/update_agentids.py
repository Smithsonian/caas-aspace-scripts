#!/usr/bin/python3
# This script takes an Excel file, "combined-aspace-agents-edited.xlsx", and uses the "combined and cleaned" sheet,
# takes the agent link, grabs the agent JSON from ArchivesSpace using the API, then adds a new Record ID to the agent,
# if the existing record ID does not exist. Record IDs are located as columns in the sheet, named "SNAC_id", "ULAN_id",
# "VIAF_id", "Wikidata_id", and "LCNAF_id". After adding the Record ID to the JSON locally, the script posts the update
# via the ArchivesSpace API.
import argparse
import os
import pandas  # TODO: update the Wiki for this script - notsosecrets.py file will not work as will cause ImportError: cannot import name randbits when loading pandas. See https://stackoverflow.com/questions/73055157/what-does-importerror-cannot-import-name-randbits-mean
import sys
import time

from copy import deepcopy
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, record_error, write_to_file

logger.remove()
log_path = Path('../logs', 'update_agentids_{time:YYYY-MM-DD}.log')  # TODO: work to change this so it goes to 1 log folder, not 2
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("excelPath", help="path to Excel input file", type=str)
    parser.add_argument("objectType", help="resources/archival_objects/digital_objects", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def add_recordID(record_id, record_source, source_index, object_json, primary=False):
    """
    Adds a record ID to the agent_record_identifiers field and record ID source to the object JSON and returns the
    updated JSON

    Args:
        record_id (str): the identifier for the object as given by the identifier's source
        record_source (str): the source for the identifier
        source_index (int): the index where the source should be added to the list of record identifiers
        object_json (dict): the original object JSON data to modify
        primary (bool): mark the record ID as the primary ID. Default is False
    Returns:
        updated_json (dict): the updated JSON with the newly added record ID
    """
    if type(record_id) != str:
        record_error(f'add_recordID() error - invalid record identifier: {record_id}', TypeError)
        raise TypeError
    elif type(record_source) != str:
        record_error(f'add_recordID() error - invalid record source: {record_source}', TypeError)
        raise TypeError
    else:
        updated_object_json = deepcopy(object_json)
        if check_ids(record_source, record_id, object_json) is None:
            new_record = {"primary_identifier": primary,
                          "record_identifier": record_id,
                          "source": record_source,
                          "jsonmodel_type": "agent_record_identifier"}
            updated_object_json["agent_record_identifiers"].insert(source_index, new_record)
            return updated_object_json


def check_ids(id_source, record_id, object_json):
    """
    Checks the given record identifier with that in ArchivesSpace. If they do not match, return False. If record
    identifiers match, return True. If no record source matches any in ArchivesSpace, return None.
    Args:
        id_source (str): the identifier source for the record being checked. Lowercase and match what's in ASpace.
        record_id (str): the identifier for the record being checked.
        object_json (dict): the object's JSON
    Returns:
        True: If record identifier
    """
    for record in object_json["agent_record_identifiers"]:
        if id_source == record["source"]:
            if record["record_identifier"] != record_id:
                record_error(f'check_ids() - Identifier in ASpace - {record["record_identifier"]} - '
                             f'does not match identifier provided - {record_id} - for {object_json["uri"]}',
                             "error: identifiers do not match")
                return False
            else:
                return True
    return None

def main(excel_location, object_type):
    """
    Takes an Excel file of agent IDs, adds the IDs to the agent JSON as Record IDs, then posts it via the ASpace API

    Args:
        excel_location (str): filepath of the Excel file with the agent IDs
        object_type (str): the type of object to be updated. In this case, "agents"
    """
    original_agent_json = Path('../logs', f'update_agentids_original_data_{time.strftime("%Y-%m-%d")}.jsonl')
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    pandas.set_option('display.max_rows', 10000)
    agent_excelfile = pandas.ExcelFile(excel_location)
    combined_and_cleaned_sheet = agent_excelfile.parse("combined and cleaned")
    combined_and_cleaned_sheet.fillna(0, inplace=True)  # replace missing cell values with 0 to sort out later - source: https://medium.com/swlh/data-science-for-beginners-how-to-handle-missing-values-with-pandas-73db5fcd46ec
    id_sources = [header for header in combined_and_cleaned_sheet.columns.values if "_id" in header]
    # print(combined_and_cleaned_sheet.duplicated(subset=["Aspace_link"]))
    for row in combined_and_cleaned_sheet[:1].itertuples():
        uri_parts = row.Aspace_link.split("/")
        original_agent_json = local_aspace.get_object(object_type, uri_parts[-1])
        updated_object_json = deepcopy(original_agent_json)
        sort_index = 0
        if original_agent_json is not None:
            print(original_agent_json["title"])  # TODO: way to do this recursively? while loop or within function?
            if row.Wikidata_id and row.Wikidata_id != 0:
                updated_object_json = add_recordID(row.Wikidata_id, "wikidata", sort_index,
                                                   updated_object_json, primary=True)
                sort_index += 1  # TODO: change the order of already existing record IDs
            if row.SNAC_id and row.SNAC_id != 0:
                updated_object_json = add_recordID(str(int(row.SNAC_id)), "snac", sort_index, updated_object_json)  # converting id to integer to remove extraneous decimal places, then convert to string
                sort_index += 1
            if row.LCNAF_id and row.LCNAF_id != 0:
                updated_object_json = add_recordID(row.LCNAF_id, "lcnaf", sort_index, updated_object_json)
                sort_index += 1
            if row.ULAN_id and row.ULAN_id != 0:
                updated_object_json = add_recordID(str(int(row.ULAN_id)), "ulan", sort_index, updated_object_json)  # converting id to integer to remove extraneous decimal places, then convert to string
                sort_index += 1
            if row.VIAF_id and row.VIAF_id != 0:
                updated_object_json = add_recordID(str(int(row.VIAF_id)), "viaf", sort_index, updated_object_json)  # converting id to integer to remove extraneous decimal places, then convert to string
        print(updated_object_json)


    # uris = read_csv(str(Path(os.getcwd(), csv_location)))
    # for row in uris:
    #     location_uri = row['uri'].split('/')
    #     location_type, location_id = location_uri[1], location_uri[2]
    #     location_data = local_aspace.get_object(location_type, location_id)
    #     write_to_file(original_location_json, location_data)
    #     updated_location = add_repo(location_data, repo_id)
    #     update_status = local_aspace.update_object(row['uri'], updated_location)
    #     if 'error' in update_status:
    #         record_error(f'main() - Error updating location {row["uri"]}', update_status)
    #     else:
    #         logger.info(update_status)
    #         print(update_status)

# Call with `python update_agentids.py <filename>.xlsx agents/people`
if __name__ == '__main__':
    main(excel_location=str(Path(f'{sys.argv[1]}')), object_type=str(f'{sys.argv[2]}'))
