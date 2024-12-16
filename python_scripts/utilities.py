#!/usr/bin/env python

import csv
import requests

from asnake.client import ASnakeClient
from asnake.client.web_client import ASnakeAuthError
from loguru import logger

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
		print(f'ERROR authorizing ASnake client: {e}')
		logger.error(f'ERROR authorizing ASnake client: {e}')
		return ASnakeAuthError
	else:
		return client
    
def read_csv(csv_file):
	"""
	Args:
		csv_file (str): filepath for the subjects csv

	Returns:
		csv_dict (list): a list of subjects to update and their metadata based on the csv contents
	"""
	csv_dict = []
	try:
		open_csv = open(csv_file, 'r', encoding='UTF-8')
		csv_dict = csv.DictReader(open_csv)
	except IOError as csverror:
		logger.error(f'ERROR reading csv file: {csverror}')
		print(f'ERROR reading csv file: {csverror}')
	else:
		return csv_dict
    
def check_url(url):
	"""
	Args:
		url (str): uri to be checked

	Returns:
		status (str): status of the request
	"""
	try:
		response = requests.head(url)
		if response.status_code == 200:
			return True
		else:
			logger.error(f'ERROR with requested url: {url}.  Status code: {response.status_code}.')
			print(f'ERROR with requested url: {url}.  Status code: {response.status_code}.')
	except requests.exceptions.RequestException as e:
		logger.error(f'ERROR fetching uri: {e}')
		print(f'ERROR fetching uri: {e}')
