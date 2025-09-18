#!/usr/bin/python3
# This script takes a CSV of archival object refIDs and runs each refID through an SQL query, which gets all associated
# digital objects with that archival object. It then returns the completed digital object URI and adds it to a list.
# Then it goes through the list of URIs and deletes them from ArchivesSpace using the delete_objects.py script.

import argparse
import csv
import os
import subprocess
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceDatabase, read_csv

logger.remove()
log_path = Path('./logs', 'delete_aaadigobjs_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to CSV input file", type=str)
    parser.add_argument("jsonPath", help="path to the JSONL file for storing data", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def update_query(arch_object_refid):
    """
    Take an archival object refID and put it in the WHERE clause of the digobj_query, return the query
    Args:
        arch_object_refid (str): the archival object refID

    Returns:
        digobj_query (tuple): string embedded tuple of the updated SQL query
    """
    if type(arch_object_refid) is not str:
        raise TypeError
    else:
        digobj_query = (f'SELECT '
                            f'CONCAT("/repositories/30/digital_objects/", digobj.id) AS URI '
                        f'FROM '
                            f'`instance` AS inst '
                                f'JOIN '
                            f'instance_do_link_rlshp AS instrel ON instrel.instance_id = inst.id '
                                f'JOIN '
                            f'archival_object AS ao ON ao.id = inst.archival_object_id '
                                f'JOIN '
                            f'digital_object AS digobj ON digobj.id = instrel.digital_object_id '
                        f'WHERE '
                            f'ao.ref_id = "{arch_object_refid}"')
        return digobj_query

def main(csv_path, jsonl_path, dry_run=False):
    """
    This script takes a CSV of archival object refIDs and runs each refID through an SQL query, which gets all
    associated digital objects with that archival object. It then returns the completed digital object URI and adds it
    to a list. Then it goes through the list of URIs and deletes them from ArchivesSpace using the delete_objects.py
    script.

    The CSV should have the following data structure:
    - Column 1 header = uri
    - Column 1 rows = /repositories/##/archival_object/#######

    Args:
        csv_path (str): filepath of the CSV file with the archival object URIs
        jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    as_database = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                 os.getenv('db_port'))
    digobjs_uris = [['uri']]
    unique_uris = []
    for refID in read_csv(csv_path):
        refid_query = update_query(refID["refID"])
        get_digobjs = as_database.query_database(refid_query)
        if get_digobjs:
            for digobj_uri in get_digobjs:
                if digobj_uri[0] not in unique_uris:
                    unique_uris.append(digobj_uri[0])
                    digobjs_uris.append([digobj_uri[0]])
        else:
            logger.info(f'Could not find and associated digital object with: {refID["refID"]}')
            print(f'Could not find and associated digital object with: {refID["refID"]}')
    with open('aaa_delete_daos.csv', 'w', encoding='UTF-8', newline='') as daofile:
        daowriter = csv.writer(daofile)
        daowriter.writerows(digobjs_uris)
        daofile.close()
    delete_dos_filepath = str(Path(os.getcwd(), 'aaa_delete_daos.csv'))
    if dry_run:
        subprocess.run(['python', '../repeatable/delete_objects.py', delete_dos_filepath, jsonl_path, '-dR'])
    else:
        subprocess.run(['python', '../repeatable/delete_objects.py', delete_dos_filepath, jsonl_path])


# Call with `python delete_aaadigobjs.py <csv_filpath>.csv <jsonl_filepath>.jsonl`
if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(csv_path=args.csvPath, jsonl_path= args.jsonPath, dry_run=args.dry_run)
