# This script collects all users from ArchivesSpace, parses their usernames to separate any starting with 'z-' and
# ending with '-expired-' into just the text in-between, then updates the username in ArchivesSpace with the new
# username
from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from collections import namedtuple
from loguru import logger
from pathlib import Path
from secrets import *
import re

username_capture = re.compile(r'(?<=z-)(.*)(?=-expired)', re.UNICODE)

logger.remove()
log_path = Path(f'../logs', 'update_znames_{time:YYYY-MM-DD}.log')
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
    # aspace = ASpace(baseurl=as_api_stag, username=as_un, password=as_pw)
    client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)
    try:
        client.authorize()
    except ASnakeAuthError as e:
        print(f'Failed to authorize ASnake client. ERROR: {e}')
        logger.error(f'Failed to authorize ASnake client. ERROR: {e}')
        return ASnakeAuthError
    else:
        return client


def get_userdata(client):
    """
    Gets all user data from ArchivesSpace client provided

    Args:
        client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API

    Returns:
        users_data (list): list of dictionaries with all users metadata in ArchivesSpace
    """
    users_data = []
    user_ids = client.get(f'/users', params={'all_ids': True}).json()
    for user_id in user_ids:
        user_data = client.get(f'/users/{user_id}').json()
        users_data.append(user_data)
    return users_data


def parse_znames(user):
    """
    Takes all user metadata, parses to see which ones have z- and -expired strings and updates usernames removing those

    Args:
        user (dict): User's metadata in ArchivesSpace

    Returns:
        updated_username (tuple): returns True if username matches or False if not, and a string of the matched username
         or error message
    """
    Update = namedtuple('Update', 'Error Message')
    if "username" in user:
        if bool(un_matches := username_capture.findall(user['username'])) is True:
            if len(un_matches) > 1:
                updated_username = Update(True, f'!!ERROR!!: More than 1 match detected in {user['username']}: '
                                                f'{un_matches}')
                return updated_username
            else:
                updated_username = Update(False, un_matches[0])
                return updated_username
        else:
            updated_username = Update(True, f'!!ERROR!!: Username does not match: {user["username"]}')
            return updated_username
    else:
        updated_username = Update(True, f'!!ERROR!!: No username found: {user}')
        print(updated_username.Message)
        logger.error(updated_username.Message)
        return updated_username


def update_usernames(client, new_username):
    """

    Args:
        client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API
        new_username (dict): the updated user metadata with new username

    Returns:
        update_message (dict): ArchivesSpace response
    """
    update_message = client.post(f'{new_username["uri"]}', json=new_username).json()
    return update_message


def main():
    """
    Runs the functions of the script, collecting, parsing, then updating user metadata in ArchivesSpace, printing
    error messages if they occur
    """
    client = client_login(as_api, as_un, as_pw)
    users_data = get_userdata(client)
    existing_usernames = [user['username'] for user in users_data]
    for user in users_data:
        parsed_username = parse_znames(user)
        if 'is_active_user' in parsed_username.Message:
            if parsed_username.Message['is_active_user'] is False:
                logger.info(f'WARNING: {user["username"]} is marked as ACTIVE, '
                            f'is_active_user: {user['is_active_user']}')
        if parsed_username.Error is True:
            if 'Username does not match' in parsed_username.Message:
                pass
            else:
                print(parsed_username.Message)
                logger.error(f'!!ERROR!!: {parsed_username.Message}')
        else:
            user['username'] = parsed_username.Message
            if parsed_username.Message in existing_usernames:
                print(f'Username already exists: {parsed_username.Message}')
                logger.error(f'Username already exists: {parsed_username.Message}')
            else:
                logger.info(f'Original user data: {user}')
                aspace_response = update_usernames(client, user)
                if 'Error' in aspace_response:
                    print(f'!!ERROR!!: {aspace_response}')
                    logger.error(aspace_response)
                else:
                    print(f'Updated user data: {parsed_username.Message}: {aspace_response}')
                    logger.info(f'{parsed_username.Message}: {aspace_response}')


if __name__ == "__main__":
    main()
