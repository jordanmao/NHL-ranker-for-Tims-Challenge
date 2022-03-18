import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')

class TimsAppConnector:
    def __init__(self):
        self.bearer_token = self.getBearerToken()

    def getBearerToken(self):
        url = 'https://cognito-idp.us-east-1.amazonaws.com/'
        payload = json.dumps({
            "ClientId": CLIENT_ID,
            "AuthFlow": "REFRESH_TOKEN_AUTH",
            "AuthParameters": {
                "REFRESH_TOKEN": REFRESH_TOKEN,
                "DEVICE_KEY": None
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
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get('AuthenticationResult').get('IdToken')
        
    def getGamesAndPlayers(self):
        url = 'https://px-api.rbi.digital/hockeyprod/picks'
        headers = {
            'authority': 'px-api.rbi.digital',
            'accept': 'application/json, text/plain, */*',
            'x-cognito-id': 'us-east-1:09dc87b6-4be2-475e-ac4c-2e00cbc11bbf',
            'authorization': f'Bearer {self.bearer_token}',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; T773O Build/RKQ1.210107.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.58 Mobile Safari/537.36',
            'origin': 'https://timhortons.ca',
            'x-requested-with': 'digital.rbi.timhortons',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://timhortons.ca/',
            'accept-language': 'en-CA,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'if-none-match': 'W/"70c-oHT3ZjjXihnpscGzW7Bm92wKG4w"'
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def submitPicks(self, player1_id, player2_id, player3_id):
        url = "https://px-api.rbi.digital/hockeyprod/picks"
        payload = json.dumps({
            "picks": [
                {
                    "setId": "1",
                    "playerId": player1_id
                },
                {
                    "setId": "2",
                    "playerId": player2_id
                },
                {
                    "setId": "3",
                    "playerId": player3_id
                }
            ]
        })
        headers = {
            'authority': 'px-api.rbi.digital',
            'accept': 'application/json, text/plain, */*',
            'x-cognito-id': 'us-east-1:09dc87b6-4be2-475e-ac4c-2e00cbc11bbf',
            'authorization': f'Bearer {self.bearer_token}',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; T773O Build/RKQ1.210107.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.58 Mobile Safari/537.36',
            'content-type': 'application/json',
            'origin': 'https://timhortons.ca',
            'x-requested-with': 'digital.rbi.timhortons',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://timhortons.ca/',
            'accept-language': 'en-CA,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6'
        }
        response = requests.post(url, headers=headers, data=payload)
        return response.status_code