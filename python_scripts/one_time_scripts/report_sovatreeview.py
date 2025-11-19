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

from bs4 import BeautifulSoup
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

def main():
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
    """
    as_database = ASpaceDatabase(os.getenv('db_un'), os.getenv('db_pw'), os.getenv('db_host'), os.getenv('db_name'),
                                 os.getenv('db_port'))
    no_aspace_eadid = []
    no_matching_eadid = []
    no_treeview = [['ead_id', 'fancytree_url']]
    no_treeview_count = 0
    page = requests.get("https://sirismm.si.edu/EADs/?C=M;O=D")
    soup = BeautifulSoup(page.content, "html.parser")
    for ead_ref in soup.find_all("a")[4:]:
        ead_id = str(ead_ref['href'][:-8])  # remove -ead.xml ending
        aspace_id_query = ('SELECT '
                           'res.ead_id, res.id '
                           'FROM '
                           '`resource` AS res '
                           'WHERE '
                          f'res.ead_id LIKE "{ead_id}"')
        get_aspace_id = as_database.query_database(aspace_id_query)
        if not get_aspace_id:
            no_aspace_eadid.append(ead_id)
        elif ead_id != get_aspace_id[0][0]:
            no_matching_eadid.append(get_aspace_id[0][0])
        else:
            aspace_id = get_aspace_id[0][1]
            treeview_url = "https://sova.si.edu/fancytree/" + ead_id
            treeview_status = has_treeview(treeview_url)
            if treeview_status is False:
                archival_objects = ('SELECT '
                                    'ao.ref_id '
                                    'FROM '
                                    'archival_object AS ao '
                                    'RIGHT JOIN '
                                    '`resource` AS res ON res.id = ao.root_record_id '
                                    'WHERE '
                                   f'ao.root_record_id = {aspace_id} '
                                    'AND ao.parent_id IS NULL '
                                    'AND ao.publish IS TRUE '
                                    'AND res.finding_aid_status_id = 261446')
                pub_aos = as_database.query_database(archival_objects)
                if pub_aos:
                    no_treeview_count += 1
                    no_treeview.append([ead_id, treeview_url])
                    print(f'{ead_id}, {treeview_url}')
                    logger.info(f'EAD with no fancytree response: {ead_id}, {treeview_url}')
    with open('sova_fancytree_report.csv', 'w', encoding='UTF-8', newline='') as csv_report:
        notree_writer = csv.writer(csv_report)
        notree_writer.writerows(no_treeview)
        csv_report.close()
    print(f'Total EADs without Treeview: {no_treeview_count}')
    logger.info(f'Total EADs without Treeview: {no_treeview_count}')
    logger.info(f'No matching EAD IDs in ASpace: {no_aspace_eadid}')
    logger.info(f'Non-matching EAD IDs: {no_matching_eadid}')


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
    main()
