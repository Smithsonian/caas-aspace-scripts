# This script collects all resources and archival objects from every repository, checks their notes for lists and
# 'Missing Title' in the list title, removes the title and updates to ArchivesSpace

from asnake.client.web_client import ASnakeAuthError

from secrets import *
from asnake.client import ASnakeClient

# TODO: add logging


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
    client = ASnakeClient(baseurl=as_api, username=as_un, password=as_pw)
    try:
        client.authorize()
    except ASnakeAuthError as e:
        print(f'Failed to authorize ASnake client. ERROR: {e}')
        return ASnakeAuthError
    else:
        return client


def delete_missingtitle(object):
    """
    Iterate through all the notes of a specific object (resource or archival object) and return object without 'Missing
    Title' in notes list titles

    Args:
        object (dict): metadata for the specific object (resource or archival_object)

    Returns:
        new_object (dict): updated metadata for object without 'Missing Title' in notes list titles
    """
    new_object = {}
    for note in object['notes']:
        if note['jsonmodel_type'] == 'note_multipart':
            if 'subnotes' in note:
                for subnote in note['subnotes']:
                    if (subnote['jsonmodel_type'] == 'note_orderedlist' or
                            subnote['jsonmodel_type'] == 'note_definedlist' or
                            subnote['jsonmodel_type'] == 'note_chronology'):
                        if 'title' in subnote:
                            if subnote['title'] == 'Missing Title':
                                print(object)
                                subnote.pop('title', None)
                                new_object = object
    return new_object


def get_objects(client, repo, object_type):
    """
    Iterate through all objects (resources or archival objects) in a given repository and return new object without
    'Missing Title' in notes lists

    Args:
        client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API
        repo (dict): metadata for a specific repository
        object_type (str): specific type of object to iterate through (resources or archival_objects)

    Returns:
        new_resobj (dict): updated object record with "Missing Title" removed from notes lists
    """
    all_res_ids = client.get(f'{repo['uri']}/{object_type}', params={'all_ids': True}).json()
    for res_id in all_res_ids:
        object_md = client.get(f'{repo['uri']}/{object_type}/{res_id}').json()
        if 'notes' in object_md:
            if bool(object_md['notes']) is True:
                new_resobj = delete_missingtitle(object_md)
                if new_resobj:
                    return new_resobj


def update_object(client, new_object, repo, object_id):
    """

    Args:
        client (ASnake.client object): client object from ASnake.client to allow to connect to the ASpace API
        new_object (dict): the updated metadata for the object
        repo (dict): metadata for a specific repository
        object_id (str): identifier of the object in ArchivesSpace

    Returns:
        update_message (dict): ArchivesSpace response
    """
    update_message = client.post(f'{repo['uri']}/resources/{object_id}', json=new_object).json()
    return update_message


def main():
    """
    Runs the functions of the script, collecting, parsing, then updating metadata in for resources and archival objects
    with notes that have 'Missing Title' in their notes list titles
    """
    client = client_login(as_api, as_un, as_pw)
    all_repos = client.get('/repositories', params={'all_ids': True}).json()
    for repo in all_repos:
        updated_resource = get_objects(client, repo, 'resources')
        print(updated_resource)
        updated_archobj = get_objects(client, repo, 'archival_objects')
        print(updated_archobj)


if __name__ == "__main__":
    main()
