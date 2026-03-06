#!/usr/bin/python3
# This script takes a CSV file containing, at minimum, a repo_id, agent_type, and
# agent_id, for a set of agents and downloads the resulting EAC-CPF representations
# of those agents to a given destination directory.
import argparse
import os
import sys

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, record_error, write_to_xml_file

logger.remove()
log_name = __file__.rsplit('/',1)[1].replace('.py', '')+'_{time:YYYY-MM-DDTHH:MM:SS}'
log_path = Path(f'./logs/{log_name}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)

def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to CSV input file", type=str)
    parser.add_argument("outputDir", help="path to the directory where EAC-CPF files should be saved", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()

def get_eac(local_aspace, row):
    agent_xml = local_aspace.aspace_client.get(f"/repositories/{row['repo_id']}/archival_contexts/{row['agent_type']}/{row['agent_id']}.xml").text
    if 'error' in agent_xml:
        record_error(f"get() - Failed to retrieve '/repositories/{row['repo_id']}/archival_contexts/{row['agent_type']}/{row['agent_id']}.xml' due to following error: ", agent_xml)
    else:
        return agent_xml

def make_or_create_file_path(output_dir, row):
    file_path = os.path.join(output_dir, f"{row['agent_type']}_{row['agent_id']}.xml")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Directory '{output_dir}' created.")
        print(f"Directory '{output_dir}' created.")
    return file_path

def main(csv_path, output_dir, dry_run=False):
    """
    Takes a CSV of agents and exports the EAC-CPF representations of those agents

    Args:
        csv_path (str): filepath of the CSV containing the agent's repo_id, type, and id
        output_dir (int): path to the directory where EAC-CPF files should be saved
        dry_run (bool): if True, it fetches the records that would be exported, but does not save them
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    agents = read_csv(str(Path(os.getcwd(), csv_path)))
    for row in agents:
        file_path = os.path.join(output_dir, f"{row['agent_type']}_{row['agent_id']}.xml")
        agent_xml = get_eac(local_aspace, row)
        if not dry_run:
            file_path = make_or_create_file_path(output_dir, row)
            write_to_xml_file(file_path, agent_xml)
        else:
            logger.info(f'The following would be written to {file_path}:\n{agent_xml}')
            print(f'The following would be written to {file_path}:\n{agent_xml}')

# Call with `python fetch_eac.py <input_filename>.csv <output_dir>`
if __name__ == '__main__':
    args = parseArguments()

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(csv_path=args.csvPath, output_dir= args.outputDir, dry_run=args.dry_run)
    