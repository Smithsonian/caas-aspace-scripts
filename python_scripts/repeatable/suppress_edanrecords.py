# This script takes a CSV of EAD IDs and suppresses the records in EDAN, removing them from view in SOVA. Optionally,
# it can also suppress the resources in ASpace if the resource URI is provided.
import argparse
import datetime
import os
import sys
from pathlib import Path

import jwt
import requests
from dotenv import find_dotenv, load_dotenv
from loguru import logger

sys.path.append(os.path.dirname('python_scripts'))  # Needed to import functions from utilities.py
from python_scripts.utilities import ASpaceAPI, read_csv, record_error

# Find  and load environment-specific .env file
env_file = find_dotenv(f'.env.{os.getenv("ENV", "dev")}')
load_dotenv(env_file)


def parseArguments():
    """Parses the arguments fed to the script from the terminal or within a run configuration"""
    parser = argparse.ArgumentParser()

    parser.add_argument("csvPath", help="path to CSV input file", type=str)
    parser.add_argument("logFolder", help="path to the log folder for storing log files", type=str)
    parser.add_argument("-sA", "--suppress-aspace", help="suppress the record in ArchivesSpace",
                        action='store_true')
    parser.add_argument("-jA", "--jwt-algorithm", help="algorithm for encoding JWT payload. Ex. HS256",
                        type=str)
    parser.add_argument("-dR", "--dry-run", help="dry run?", action='store_true')
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    return parser.parse_args()


def prepare_edan_data(jwt_algorithm="HS256"):
    """
    Prepares the EDAN payload and returns encoded JSON web token

    Args:
        jwt_algorithm (str): the JSON Web Token algorithm used to encode the payload to EDAN. Default: HS256

    Returns:
        encoded_jwt (jtw): the encoded JSON web token
    """
    # time = datetime.datetime.now(datetime.UTC)
    # NOTE: below added a 5 second timedelta due to error with authenticating against EDAN being too strict. Potential
    # to replace code below when EDAN fix is completed with the above code.
    time = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=5)
    payload = {"iss": os.getenv('edan_iss'),
               "jwtid": os.getenv('edan_jwtid'), #should be unique. not as yet enforced
               "iat": time}

    # Encode the JWT
    try:
        encoded_jwt = jwt.encode(payload, os.getenv('edan_key'), algorithm=jwt_algorithm)
    except EncodingWarning as encode_error:
        record_error('prepare_edan_data() error: An error occurred when encoding JWT', encode_error)
    except NotImplementedError as algorithm_error:
        record_error('prepare_edan_data() error: An error occurred with the algorithm provided',
                     algorithm_error)
    else:
        return encoded_jwt


def main(csvPath, aspace_suppress=False, jwt_algorithm=None, dry_run=False):
    """
    This script takes a CSV of EAD IDs and suppresses the records in EDAN, removing them from view in SOVA. Optionally,
    it can also suppress the resources in ASpace if the resource URI is provided.

    The CSV should have the following columns:
    - eadID, ex: NAA.2009-07
    - resourceURI, ex. /repositories/36/resource/12345 (optional - only needed if suppressing records in ASpace)

    Args:
        csvPath (str): filepath of the CSV file containing all EAD IDs to suppress in EDAN
        aspace_suppress (bool): if True, suppress the records indicated in the provided CSV
        jwt_algorithm (str): if not None, use the provided algorithm for encoding the payload to EDAN
        dry_run (bool): if True, it prints the prepared EDAN post but does not post to EDAN
    """
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))
    for ead_row in read_csv(csvPath):
        if jwt_algorithm:
            encoded_jwt = prepare_edan_data(jwt_algorithm)
        else:
            encoded_jwt = prepare_edan_data()
        if encoded_jwt is not None:
            #print(f"Encoded JWT: {encoded_jwt}")

            # Set up the headers with the JWT
            headers = {"Authorization": f"Bearer {encoded_jwt}",
                       "Content-Type": "application/json"}

            # Right now, the suppressed action is inferred for the eadTask endpoint, so all you need to do is pass the
            # EAD ID

            post_data = {"id": str(ead_row['eadID'])}
            if dry_run:
                print(f'The following post would be made to EDAN: headers={headers}, json={post_data}')
            else:
                response = requests.post(os.getenv('edan_api'), headers=headers, json=post_data)

                # Check the response
                if response.status_code == 200:
                    print(f'Request successful! Response data: {response.json()}')
                    logger.info(f'Request successful! Response data: {response.json()}')
                else:
                    print(f"main() error: Request failed with status code: {response.status_code}\n{response.text}")
                    logger.error(f'main() error: Request failed with status code {response.status_code} - '
                                 f'{response.text}')
        if aspace_suppress:
            if dry_run:
                print(f'The following resource would be suppressed: {ead_row['resourceURI']}')
                logger.info(f'The following resource would be suppressed: {ead_row['resourceURI']}')
            else:
                suppress_response = local_aspace.update_suppression(ead_row['resourceURI'], True)
                if suppress_response is not None:
                    print(f'main() - suppressed object: {ead_row['resourceURI']}: {suppress_response}')
                    logger.info(f'main() - suppressed object: {ead_row['resourceURI']}: {suppress_response}')


# Call with `python suppress_edanrecords.py <input_filename>.csv <logfile_path>.log`
if __name__ == '__main__':
    args = parseArguments()

    # Set up log file
    logger.remove()
    log_path = Path(args.logFolder, 'suppress_edanrecords_{time:YYYY-MM-DDTHH-MM-SS}.log')
    logger.add(str(log_path), format="{time}-{level}: {message}")

    # Print arguments
    logger.info(f'Running {sys.argv[0]} script with following arguments: ')
    print(f'Running {sys.argv[0]} script with following arguments: ')
    for arg in args.__dict__:
        logger.info(str(arg) + ": " + str(args.__dict__[arg]))
        print(str(arg) + ": " + str(args.__dict__[arg]))

    # Run function
    main(csvPath=args.csvPath, aspace_suppress=args.suppress_aspace, jwt_algorithm=args.jwt_algorithm,
         dry_run=args.dry_run)
