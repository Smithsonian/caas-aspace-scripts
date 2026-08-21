# TODO: Fill out
import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from loguru import logger

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import read_csv

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)


def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to CSV input file", type=str)
    parser.add_argument("logFolder", help="path to the log folder for storing log files", type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()


def sirismm_removal(ead_id):

    subprocess.run(['rm', '/sirismm/siris/sirispublic/EADs/$rec_id-ead.xml'], check=False)
    subprocess.run(['rm', '/sirismm/siris/sirispublic/EADpdfs/$rec_id.pdf'], check=False)
    # subprocess.run(['rm', '/sirismm/siris/sirispublic/EACs/$rec_id-eac.xml'])


def dropbox_removal(ead_id):
    testdropbox = "/data/load_test/SOVA"
    print(testdropbox)
    print(f"******************** DELETING {ead_id}-ead.xml      from    /lassb-data/SOVA/eads/      ***************")
    subprocess.run(['rm', '-r', '"/lassb-data/SOVA/eads/$rec_id-ead.xml"'], check=False)

    print(f"******************** DELETING {ead_id}-ead.xml  from    /lassb-data/SOVA/idxfiles/  ***************")
    subprocess.run(['rm', '-r', '"/lassb-data/SOVA/idxfiles/$rec_id-ead-idx.xml"'], check=False)

    print(f"******************** DELETING {ead_id}-ead-uidx.xml from    /lassb-data/SOVA/idxfiles/  ***************")
    subprocess.run(['rm', '-r', '"/lassb-data/SOVA/idxfiles/$rec_id-ead-uidx.xml"'], check=False)

    print(f"******************** DELETING {ead_id}.pdf          from    /lassb-data/SOVA/pdfs/      ***************")
    subprocess.run(['rm', '-r', '"/lassb-data/SOVA/pdfs/$rec_id.pdf"'], check=False)

    # print(f"******************** DELETING {ead_id}-eac.xml      from    /lassb-data/EAC/eacs/       ***************")
    # subprocess.run(['rm', '-r', "/lassb-data/EAC/eacs/$rec_id-eac.xml"])
    #
    # print(f"******************** DELETING {ead_id}-eac-idx.xml  from    /lassb-data/EAC/idxfiles/   ***************")
    # subprocess.run(['rm', '-r', '"/lassb-data/EAC/idxfiles/$rec_id-eac-idx.xml"'])

    print(f"******************** DELETING {ead_id}-eadingestrequest.xml  from    /lassb-data/SOVA/eadIngestRequests/   ***************")
    subprocess.run(['rm', '-r', '"/lassb-data/SOVA/eadIngestRequests/$rec_id-eadingestrequest.xml"'], check=False)

    print(f"******************** DELETING {ead_id}-ead.xml  from    /qsova-dropbox/test_OCIO/RawEADArchive/   ***************")
    subprocess.run(['rm', '-r', '"/qsova-dropbox/test_OCIO/RawEADArchive/$rec_id-ead.xml"'], check=False)

    print(f"******************** DELETING {ead_id}-ead.xml  from    /qsova-dropbox/test_OCIO/EADarchives/EADarchiveYYYY-MM-DD/   ***************")
    subprocess.run(['rm', '-r', '"/qsova-dropbox/test_OCIO/EADarchives/EADarchive*/$rec_id-ead.xml"'], check=False)


def main(csvPath, dry_run=False):
    """
    # TODO: Fill out

    Args:
        # TODO: Fill out
    """
    for ead_row in read_csv(csvPath):
        print(ead_row)


# Call with `python remove_edanrecords.py <input_filename>.csv <logfile_path>.log`
if __name__ == '__main__':
    args = parseArguments()

    # Set up log file
    logger.remove()
    log_path = Path(args.logFolder, 'remove_edanrecords_{time:YYYY-MM-DDTHH-MM-SS}.log')
    logger.add(str(log_path), format="{time}-{level}: {message}")

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(csvPath=args.csvPath, dry_run=args.dry_run)
