import os
import sys
import json
import logging
import requests
from requests.exceptions import HTTPError
from autopicker.utils.logger_utils import log_http_error
from dotenv import load_dotenv


# Initialize a logger for TimsAppApiClient
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
USER_AGENT = os.getenv('USER_AGENT')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
USER_ID = os.getenv('USER_ID')

if CLIENT_ID == None:
    logger.error('CLIENT_ID not found')
    sys.exit()
if USER_AGENT == None:
    logger.error('USER_AGENT not found')
    sys.exit()
if REFRESH_TOKEN == None:
    logger.error('REFRESH_TOKEN not found')
    sys.exit()
if USER_ID == None:
    logger.error('USER_ID not found')
    sys.exit()


class TimsAppApiClient:
    def __init__(self):
        bearer_token = self._get_bearer_token()
        self._access_token: str = bearer_token['AccessToken']
        self._id_token: str = bearer_token['IdToken']
        self._email: str = self._get_email()

    def _get_bearer_token(self) -> str:
        url = 'https://cognito-idp.us-east-1.amazonaws.com/'
        payload = json.dumps({
            'ClientId': CLIENT_ID,
            'AuthFlow': 'REFRESH_TOKEN_AUTH',
            'AuthParameters': {
                'REFRESH_TOKEN': REFRESH_TOKEN,
                'DEVICE_KEY': None
            }
        })
        headers = {
            'content-type': 'application/x-amz-json-1.1',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'x-amz-target': 'AWSCognitoIdentityProviderService.InitiateAuth',
            'x-amz-user-agent': 'aws-amplify/0.1.x js'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            bearer_token = response.json()['AuthenticationResult']
            logger.debug('Bearer token: ' + json.dumps(bearer_token))
            return bearer_token
        except HTTPError as http_err:
            error_msg = 'HTTP error occurred when trying to obtain bearer token'
            log_http_error(error_msg, logger, response, http_err)
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            exit()
    
    def _get_email(self) -> str:
        url = 'https://cognito-idp.us-east-1.amazonaws.com/'
        payload = json.dumps({
            'AccessToken': self._access_token
        })
        headers = {
            'authority': 'cognito-idp.us-east-1.amazonaws.com',
            'accept': '*/*',
            'accept-language': 'en-CA,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-amz-json-1.1',
            'origin': 'https://timhortons.ca',
            'referer': 'https://timhortons.ca/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': USER_AGENT,
            'x-amz-target': 'AWSCognitoIdentityProviderService.GetUser',
            'x-amz-user-agent': 'aws-amplify/5.0.4 js',
            'x-requested-with': 'digital.rbi.timhortons'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            email = response.json()['UserAttributes'][1]['Value']
            logger.info('Email: ' + email)
            return email
        except HTTPError as http_err:
            error_msg = 'HTTP error occurred when trying to obtain email'
            log_http_error(error_msg, logger, response, http_err)
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            exit()

    def get_games_and_players(self):
        url = 'https://px-api.rbi.digital/hockeyprod/picks'
        headers = {
            'authority': 'px-api.rbi.digital',
            'accept': 'application/json, text/plain, */*',
            'x-cognito-id': USER_ID,
            'authorization': f'Bearer {self._id_token}',
            'user-agent': USER_AGENT,
            'origin': 'https://timhortons.ca',
            'x-requested-with': 'digital.rbi.timhortons',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://timhortons.ca/',
            'accept-language': 'en-CA,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'if-none-match': 'W/"70c-oHT3ZjjXihnpscGzW7Bm92wKG4w"'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            logger.info('Obtained game schedule and player sets from Tim Hortons app')
            return response.json()
        except HTTPError as http_err:
            if response.json().get('code') and response.json()['code'] == 'noContest':
                logger.info('No contest available at the moment')
                return response.json()
            error_msg = 'HTTP error occurred when trying to get games schedule and players sets from Tim Hortons app'
            log_http_error(error_msg, logger, response, http_err)
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            exit()

    def get_pick_history(self):
        url = 'https://px-api.rbi.digital/hockeyprod/picks/history'
        headers = {
            'authority': 'px-api.rbi.digital',
            'accept': 'application/json, text/plain, */*',
            'x-cognito-id': USER_ID,
            'authorization': f'Bearer {self._id_token}',
            'user-agent': USER_AGENT,
            'origin': 'https://timhortons.ca',
            'x-requested-with': 'digital.rbi.timhortons',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://timhortons.ca/',
            'accept-language': 'en-CA,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'if-none-match': 'W/"105c6-5dy/kNv3YXGLEjopauej4m96XwA"'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            logger.info('Obtained pick history from Tim Hortons app')
            return response.json()
        except HTTPError as http_err:
            error_msg = 'HTTP error occurred when trying to get pick history from Tim Hortons app'
            log_http_error(error_msg, logger, response, http_err)

    def submit_picks(self, picks):
        [player1_id, player2_id, player3_id] = picks
        url = 'https://px-api.rbi.digital/hockeyprod/picks'
        payload = json.dumps({
            'picks': [
                {
                    'setId': '1',
                    'playerId': player1_id
                },
                {
                    'setId': '2',
                    'playerId': player2_id
                },
                {
                    'setId': '3',
                    'playerId': player3_id
                }
            ]
        })
        headers = {
            'authority': 'px-api.rbi.digital',
            'accept': 'application/json, text/plain, */*',
            'x-cognito-id': USER_ID,
            'authorization': f'Bearer {self._id_token}',
            'user-agent': USER_AGENT,
            'content-type': 'application/json',
            'origin': 'https://timhortons.ca',
            'x-requested-with': 'digital.rbi.timhortons',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://timhortons.ca/',
            'accept-language': 'en-CA,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            logger.info('Submitted picks to Tim Hortons app')
            return response.status_code
        except HTTPError as http_err:
            error_msg = 'Failed to submit picks to Tim Hortons app with response'
            log_http_error(error_msg, logger, response, http_err)
        