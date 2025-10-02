#!/usr/bin/python3
# This script finds resource records with a finding aid status of "Publish (sync with EDAN/SOVA)" and that have a
# published archival object on the highest level component (c01), takes the list of EAD IDs from those resources,
# and tests them against "https://sova.si.edu/fancytree/", seeing if they return an empty treeview in SOVA. If so, the
# EAD ID and fancytree URL is logged in a CSV output file.

import argparse
import csv
import os
import requests
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceDatabase

logger.remove()
log_path = Path('./logs', 'report_sovatreeview_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    # parser.add_argument("csvPath", help="path to CSV input file", type=str)
    # parser.add_argument("jsonPath", help="path to the JSONL file for storing data", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def has_treeview(url):
    """
    Takes a treeview URL and returns True if the status code is 200 and False if anything other than 200.
    Args:
        url:

    Returns:
        treeview_status (bool): the treeview status, True if it has a treeview, False if not.
    """
    treeview_response = requests.get(url)
    if not treeview_response.json():
        return False
    else:
        return True

def main(dry_run=False):
    """
    This script finds resource records with a finding aid status of "Publish (sync with EDAN/SOVA)" and that have a
    published archival object on the highest level component (c01), takes the list of EAD IDs from those resources,
    and tests them against "https://sova.si.edu/fancytree/", seeing if they return an empty treeview in SOVA. If so, the
    EAD ID and fancytree URL is logged in a CSV output file.

    The CSV output will have the following data structure:
    - Column 1 header = ead_id
    - Column 1 rows = aaa.bartmace
    - Column 2 header = fancytree_url
    - Column 2 rows = https://sova.si.edu/fancytree/aaa.bartmace

    Args:
        # csv_path (str): filepath of the CSV file with the archival object URIs
        # jsonl_path (str): filepath of the jsonL file for storing JSON data of objects before updates - backup
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    as_database = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                 os.getenv('db_port'))
    published_resources = ('SELECT '
                               'res.ead_id AS eadid, res.id '
                           'FROM '
                               'archival_object AS ao '
                                   'RIGHT JOIN '
                               'resource AS res ON res.id = ao.root_record_id '
                           'WHERE '
                               'res.publish IS TRUE '
                                   'AND res.finding_aid_status_id = 261446 '
                                   'AND ao.root_record_id IS NOT NULL '
                                   'AND ao.repo_id != 11 '
                                   'AND ao.repo_id != 23 '
                                   'AND ao.repo_id != 50 '
                           'GROUP BY res.ead_id, res.id '
                           'ORDER BY res.ead_id ASC')
    pub_res_waos = as_database.query_database(published_resources)
    no_treeview = [['ead_id', 'fancytree_url']]
    no_treeview_count = 0
    for ead_id in pub_res_waos:
        treeview_url = "https://sova.si.edu/fancytree/" + str(ead_id[0])
        treeview_status = has_treeview(treeview_url)
        if treeview_status is False:
            archival_objects = ('SELECT '
                                'ao.ref_id '
                                'FROM '
                                'archival_object AS ao '
                                'WHERE '
                                f'ao.root_record_id = {ead_id[1]} '
                                'AND ao.parent_id IS NULL '
                                'AND ao.publish IS TRUE')
            pub_aos = as_database.query_database(archival_objects)
            if pub_aos:
                no_treeview_count += 1
                no_treeview.append([ead_id[0], treeview_url])
                print(f'{ead_id[0]}, {treeview_url}')
                logger.info(f'EAD with no fancytree response: {ead_id[0]}, {treeview_url}')
    with open('sova_fancytree_report.csv', 'w', encoding='UTF-8', newline='') as csv_report:
        notree_writer = csv.writer(csv_report)
        notree_writer.writerows(no_treeview)
        csv_report.close()
    print(f'Total EADs without Treeview: {no_treeview_count}')
    logger.info(f'Total EADs without Treeview: {no_treeview_count}')


# Call with `python report_sovatreeview.py`
if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(dry_run=args.dry_run)
