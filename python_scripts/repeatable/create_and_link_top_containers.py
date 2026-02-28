# This script creates new top containers in bulk and links as instances to other records
import argparse
import csv
import os
import sys

from datetime import date
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv

logger.remove()
log_path = Path('./logs', 'create_and_link_top_containers_{time:YYYY-MM-DDTHH:MM:SS}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvInPath", help="path to CSV input file", type=str)
    parser.add_argument("csvOutPath", help="path to CSV output file", type=str)
    parser.add_argument("repoId", help="repo id for new locations", type=int)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def build_tc_query(row):
    """
    Builds out the new top container based on csv data.

    Args:
        row (dict): tc metadata from csv

    Returns:
        query (dict): an advanced query that will search top containers by barcode and indicator
    """
    query = {
            'jsonmodel_type': 'advanced_query',
            'query': { 
                'jsonmodel_type': 'boolean_query',
                'op':'AND',
                'subqueries': [
                    { 
                        'jsonmodel_type': 'field_query',
                        'field': 'barcode_u_icusort',
                        'value': row['top_container_barcode']
                    },
                    {
                        'jsonmodel_type': 'field_query',
                        'field': 'indicator_u_icusort',
                        'value': row['top_container_indicator'],
                        'literal': True
                    }
                ]
            }
        }
    
    return query
    
def build_tc(tc):
    """
    Builds out the new top container based on csv data.

    Args:
        tc (dict): tc metadata from csv

    Returns:
        data (dict): new tc ready to post to ArchivesSpace
    """
    data = {}
    data['barcode'] = tc['top_container_barcode']
    data['indicator'] = tc['top_container_indicator']
    data['type'] = tc['top_container_type']
    if tc['container_profile_id']:
        data['container_profile'] = { 'ref': f"/container_profiles/{tc['container_profile_id']}" }
    if tc['location_id']:
        data['container_locations'] = [
            {
                'status': 'current',
                'start_date': str(date.today()),
                'ref': f"/locations/{tc['location_id']}"
            }
        ]

    return data
    
def build_updated_rec(rec, tc_uri, row):
    """
    Builds out the updated resource/ao record based on csv data and a link to the new tc.
    This will preserve any existing instances and merely add additional ones to the record.

    Args:
        rec (dict): existing resource or archival object record
        tc_uri (str): uri for the just-created top container
        row (str): instance information from the csv

    Returns:
        rec (dict): new tc ready to post to ArchivesSpace
    """
    rec['instances'].append(
        {
            'instance_type': row['instance_type'],
            'sub_container': {
                'indicator_2': row['child_indicator'],
                'type_2': row['child_type'],
                'top_container': { 'ref': tc_uri }

            }
        }
    )

    return rec

def main(csv_in_path, csv_out_path, repo_id, dry_run=False):
    """
    This script takes a CSV of top container data, creates those new top containers, and
    (optionally) links those new top containers to an archival object or resource.

    The CSV should have the following columns:
    - link_to_uri (optional), ex: /repositories/2/archival_objects/1
    - instance_type (optional), ex: mixed materials [mixed materials]
    - top_container_type (optional), ex: Box [box]
    - top_container_indicator, ex: 1
    - top_container_barcode (optional), ex: 123456
    - container_profile_id (optional), ex: 1
    - child_type (optional), ex: Folder [folder]
    - child_indicator (optional), ex: 1
    - child_barcode (optional), ex: 1234567
    - location_id (optional), ex: 1
    
    Args:
        csv_in_path (str): filepath of the CSV file with top container, instance, and linked object data
        csv_out_path (str): filepath of the CSV to log to
        repo_id (int): repo_id of the locations to be created
        dry_run (bool): if True, it prints the changed object_json but does not post the changes to ASpace
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    with open(csv_out_path, mode='w', newline='', encoding='utf-8') as outfile:
        for row in read_csv(csv_in_path):
            row['mode'] = 'test update' if dry_run else 'updated'
            top_container_uri = ''
            record_to_link = row['link_to_uri']

            # Find existing or create new top_container
            query = build_tc_query(row)
            existing_tc = local_aspace.search_objects(query, 'top_container', repo_id)
            if existing_tc:
                top_container_uri = existing_tc[0]['uri']
            else:
                data = build_tc(row)
                if not dry_run:
                    post_response = local_aspace.update_object(f'/repositories/{repo_id}/top_containers', data)
                    logger.info(post_response)
                    print(post_response)
                    top_container_uri = post_response['uri']
                else:
                    top_container_uri = data
                    logger.info(f'The following top container would be created:\n{top_container_uri}')
                    print(f'The following top container would be created:\n{top_container_uri}')
            row['top_container_uri'] = top_container_uri

            # Create instance and link if we have a record to link to
            if record_to_link and top_container_uri is not None:
                if not dry_run:
                    parts = record_to_link.split('/')
                    record_to_link = local_aspace.get_object(parts[3], parts[4], f'{parts[1]}/{parts[2]}/')
                    rec_data = build_updated_rec(record_to_link, top_container_uri, row)
                    record_to_link_uri = record_to_link['uri']
                    rec_post_response = local_aspace.update_object(record_to_link['uri'], rec_data)
                    logger.info(rec_post_response)
                    print(rec_post_response)
                else:
                    record_to_link_uri = record_to_link
                    logger.info(f'and linked to:\n{record_to_link_uri}')
                    print(f'and linked to:\n{record_to_link_uri}')
                row['updated_record_uri'] = record_to_link_uri
            
            writer = csv.DictWriter(outfile, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)

# Call with `python create_and_link_top_containers.py <input_filename>.csv <output_filename>.csv <repo_id>`
if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(csv_in_path=args.csvInPath, csv_out_path=args.csvOutPath, repo_id=args.repoId, dry_run=args.dry_run)
