#!/usr/bin/python3
# This script takes an Excel file, "combined-aspace-agents-edited.xlsx", and uses the "combined and cleaned" sheet,
# takes the agent link from the "Aspace_link" column, grabs the agent JSON from ArchivesSpace using the API, then adds
# a new Record ID to the agent, if an existing record ID does not already exist. Non-matching record IDs are logged and
# the one existing in ArchivesSpace remains. Record IDs are located as columns in the sheet, named "Wikidata_id",
# "SNAC_id", "LCNAF_id", "ULAN_id", "VIAF_id", and "local". After adding the Record ID to the JSON locally, the script
# sorts the order of the IDs according to the above and posts the updated agent record via the ArchivesSpace API.
import argparse
import os
import pandas  # TODO: update the Wiki for this script - secrets.py file will not work as will cause ImportError: cannot import name randbits when loading pandas. See https://stackoverflow.com/questions/73055157/what-does-importerror-cannot-import-name-randbits-mean
import sys
import time

from collections import namedtuple
from copy import deepcopy
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, record_error, write_to_file

logger.remove()
log_path = Path('../../logs', 'update_agentids_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

SOURCES_ORDERED = ["wikidata", "snac", "naf", "ulan", "viaf", "local"]

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("excelPath", help="path to Excel input file", type=str)
    parser.add_argument("objectType", help="resources/archival_objects/digital_objects", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def add_recordID(record_id, record_source, object_json, primary=False):
    """
    Adds a record ID to the agent_record_identifiers field and record ID source to the object JSON and returns the
    updated JSON

    Args:
        record_id (str): the identifier for the object as given by the identifier's source
        record_source (str): the source for the identifier
        object_json (dict): the original object JSON data to modify
        primary (bool): mark the record ID as the primary ID. Default is False
    Returns:
        object_json (dict): the updated JSON with the newly added record ID
    """
    if type(record_id) != str:
        record_error(f'add_recordID() error - invalid record identifier: {record_id}', TypeError)
        raise TypeError
    elif record_source not in SOURCES_ORDERED:
        record_error(f'add_recordID() error - invalid record source: {record_source}', ValueError)
        raise ValueError
    else:
        id_exists = check_ids(record_source, record_id, object_json)
        if id_exists.Status is None:
            new_record = {"primary_identifier": primary,
                          "record_identifier": record_id,
                          "source": record_source,
                          "jsonmodel_type": "agent_record_identifier"}
            object_json["agent_record_identifiers"].append(new_record)
    return object_json


def check_ids(id_source, record_id, object_json):
    """
    Checks the given record identifier with that in ArchivesSpace. If they do not match, return False. If record
    identifiers match, return True. If no record source matches any in ArchivesSpace, return None.
    Args:
        id_source (str): the identifier source for the record being checked. Lowercase and match what's in ASpace.
        record_id (str): the identifier for the record being checked.
        object_json (dict): the object's JSON
    Returns:
        ID_Exists(NamedTuple): If record identifier already exists, return True and the record. If record
        source/identifier does not exist, return None, None. If the record source exists but the identifiers do not
        match between the supplied object JSON and record_id, return False and the record.
    """
    ID_Exists = namedtuple('ID_Exists', 'Status Record')
    for record in object_json["agent_record_identifiers"]:
        if id_source == record["source"]:
            if record["record_identifier"] != record_id:
                record_error(f'check_ids() - Identifier in ASpace - {record["source"]}: {record["record_identifier"]} - '
                             f'does not match identifier provided - {id_source}: {record_id} - for {object_json["uri"]}',
                             "error: identifiers do not match")
                return ID_Exists(False, record)
            else:
                return ID_Exists(True, record)
    return ID_Exists(None, None)


def sort_identifiers(object_json):
    """
    Sorts the record identifiers according to the given sort list
    Args:
        object_json (dict): the object's JSON data

    Returns:
        object_json (dict): the updated JSON with the sorted record identifiers
    """
    updated_order = [None, None, None, None, None, None]
    current_order = {record["source"]:record for record in object_json["agent_record_identifiers"]}
    for source, record_json in current_order.items():  # TODO: I wonder if I couldn't use something better for this, like lambda or a better use of filter()
        if source in SOURCES_ORDERED:
            updated_order[SOURCES_ORDERED.index(source)] = record_json
        else:
            record_error(f'sort_identifiers() - source provided does not match sources listed: {SOURCES_ORDERED} - {source}', record_json)
    updated_order_no_nones = list(filter(None, updated_order))
    object_json["agent_record_identifiers"] = updated_order_no_nones
    return object_json

def set_primary(object_json):
    """
    Sets the primary record ID for the first record in the agent_record_identifiers list, sets all other record IDs
    primary = False
    Args:
        object_json (dict): the object's JSON data

    Returns:
        object_json (dict): the updated JSON with the corrected primary record identifiers
    """
    index = 0
    for record in object_json["agent_record_identifiers"]:
        if index == 0:
            record["primary_identifier"] = True
        else:
            record["primary_identifier"] = False
        index += 1
    return object_json

def main(excel_path, object_type, dry_run=False):
    """
    Takes an Excel file of agent IDs, adds the IDs to the agent JSON as Record IDs, then posts it via the ASpace API

    Args:
        excel_path (str): filepath of the Excel file with the agent IDs
        object_type (str): the type of object to be updated. In this case, "agents"
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace or in the
        jsonlines file
    """
    original_agent_json_data = Path('../../logs', f'update_agentids_original_data_{time.strftime("%Y-%m-%d")}.jsonl')
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    # pandas.set_option('display.max_rows', 10000)  # Optional for running the script locally to see all returns
    agent_excelfile = pandas.ExcelFile(excel_path)
    combined_and_cleaned_sheet = agent_excelfile.parse("combined and cleaned")
    combined_and_cleaned_sheet.fillna(0, inplace=True)  # replace missing cell values with 0 to sort out later - source: https://medium.com/swlh/data-science-for-beginners-how-to-handle-missing-values-with-pandas-73db5fcd46ec
    for row in combined_and_cleaned_sheet.itertuples():
        uri_parts = row.Aspace_link.split("/")
        original_agent_json = local_aspace.get_object(object_type, uri_parts[-1])
        if original_agent_json:
            updated_object_json = deepcopy(original_agent_json)
            if row.Wikidata_id and row.Wikidata_id != 0:  # TODO: way to do this recursively? while loop or within function?
                updated_object_json = add_recordID(row.Wikidata_id, "wikidata", updated_object_json,
                                                   primary=True)
            if row.SNAC_id and row.SNAC_id != 0:
                updated_object_json = add_recordID(str(int(row.SNAC_id)), "snac", updated_object_json)  # converting id to integer to remove extraneous decimal places, then convert to string
            if row.LCNAF_id and row.LCNAF_id != 0:
                updated_object_json = add_recordID(row.LCNAF_id, "naf", updated_object_json)
            if row.ULAN_id and row.ULAN_id != 0:
                updated_object_json = add_recordID(str(int(row.ULAN_id)), "ulan", updated_object_json)  # converting id to integer to remove extraneous decimal places, then convert to string
            if row.VIAF_id and row.VIAF_id != 0:
                if "viaf/" in str(row.VIAF_id):
                    updated_object_json = add_recordID(str(int(row.VIAF_id[5:])), "viaf", updated_object_json)  # converting id to integer to remove extraneous decimal places, then convert to string
                # if not row.Wikidata_id and not row.SNAC_id and not row.LCNAF_id and not row.ULAN_id:
                #     print(f'ASpace Link: {row.Aspace_link}, ASpace Name: {row.name_entry}, VIAF ID: {row.VIAF_id}')
                else:
                    updated_object_json = add_recordID(str(int(row.VIAF_id)), "viaf", updated_object_json)  # converting id to integer to remove extraneous decimal places, then convert to string
            sorted_sources = sort_identifiers(updated_object_json)
            updated_primary_identifiers = set_primary(sorted_sources)
            if dry_run is True:
                print(f'{updated_primary_identifiers}')
            else:
                write_to_file(str(original_agent_json_data), original_agent_json)
                update_status = local_aspace.update_object(f'{object_type}/{uri_parts[-1]}',
                                                           updated_primary_identifiers)
                if 'error' in update_status:
                    record_error(f'main() - Error updating agent {row.Aspace_link}', update_status)
                else:
                    logger.success(update_status)
                    print(update_status)


# Call with `python update_agentids.py <filename>.xlsx agents/people`
if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(excel_path=str(Path(f'{sys.argv[1]}')), object_type=str(f'{sys.argv[2]}'))
