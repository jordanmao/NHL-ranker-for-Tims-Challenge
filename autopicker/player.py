import requests
from requests.exceptions import HTTPError
import json
import logging
from utils.logger_utils import log_http_error
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path


project_path = Path(__file__).parent.parent

# Initialize a logger for Player
logger = logging.getLogger(__name__)

class Player(object):
    injured_players = []
    recent_goal_scorers = Counter()
    time_range = 5

    def __init__(self, tims_player_data, games_today):
        # NHL player id different from the player id Tim Hortons uses
        self.id = None
        self.tims_player_id = tims_player_data['id']
        self.first_name = tims_player_data['firstName']
        self.last_name = tims_player_data['lastName']
        self.full_name = self.first_name + ' ' + self.last_name
        self.number = self._get_player_number(tims_player_data)
        self.position = tims_player_data['position']
        # NHL team id different from the team id Tim Hortons uses
        self.team_id = None
        self.tims_team_id = tims_player_data['teamId']
        self.team_abbr = None
        self.goals = 0
        self.recent_goals = 0
        self.points = 0
        self.shots = 0
        self.games = 0
        self.plus_minus = 0
        self.shot_percentage = 0
        self.time_on_ice = 0
        self.goals_per_game = 0
        self.injured = False

        self.get_nhl_team_info(games_today)
        self.get_nhl_id()
        self.get_player_stats()

    def _get_player_number(self, tims_player_data):
        # Check if player is listed in data/player_number_fixes.json file
        with open(f'{project_path}/autopicker/data/player_number_fixes.json') as f:
            player_number_fixes = json.load(f)
            for player in player_number_fixes:
                if player['timsId'] == self.tims_player_id:
                    return player['number']
        return int(tims_player_data['number'])

    def get_nhl_team_info(self, games_today):
        # In order to get the player's team NHL ID from its Tim Hortons ID, first we must 
        # obtain the team's name
        team_name = ''
        for game in games_today:
            home_team = game['teams']['home']
            away_team = game['teams']['away']
            if home_team['id'] == self.tims_team_id:
                team_name = home_team['name']
                break
            elif away_team['id'] == self.tims_team_id:
                team_name = away_team['name']
                break
        if team_name == '':
            fail_message(f"Failed to find {self.full_name}'s team name")
            logger.error(fail_message)
            raise Exception(fail_message)

        # Obtain list of all the teams in the NHL so we can get their NHL ID
        url = 'https://statsapi.web.nhl.com/api/v1/teams'
        teams = requests.get(url).json()['teams']
        for team in teams:
            if team["teamName"] == team_name:
                self.team_id = team['id']
                self.team_abbr = team['abbreviation']
                logger.debug(f"Found {self.full_name}'s team info")
                return
        fail_message = f"Failed to find {self.full_name}'s team info"
        logger.error(fail_message)
        raise Exception(fail_message)

    def get_nhl_id(self):
        url = f'https://statsapi.web.nhl.com/api/v1/teams/{self.team_id}/roster'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError as http_err:
            error_msg = f"HTTP error occured when trying to obtain team {self.team_id}'s roster"
            log_http_error(error_msg, logger, response, http_err)
        else:
            roster = response.json()['roster']
            for player in roster:
                if int(player['jerseyNumber']) == self.number:
                    self.id = player['person']['id']
                    logger.debug(f"Found {self.full_name}'s NHL id: {self.id}")
                    return
            fail_message = f"Failed to find {self.full_name}'s NHL id in {self.team_abbr} ({self.team_id})'s roster data"
            logger.error(fail_message)
            raise Exception(fail_message)

    def get_player_stats(self):
        url = f'https://statsapi.web.nhl.com/api/v1/people/{self.id}/stats?stats=statsSingleSeason&season=20222023'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError as http_err:
            error_msg = f"HTTP error occurred when trying to trying to obtain {self.full_name} ({self.id})'s stats"
            log_http_error(error_msg, logger, response, http_err)
        else:
            player_data = response.json()
            if player_data['stats'][0]['splits']:
                player_stats = player_data['stats'][0]['splits'][0]['stat']
                self.goals = player_stats['goals']
                self.recent_goals = Player.recent_goal_scorers[self.full_name]
                self.points = player_stats['points']
                self.shots = player_stats['shots']
                self.shot_percentage = player_stats['shotPct']
                self.plus_minus = player_stats['plusMinus']
                self.time_on_ice = '00:' + player_stats['timeOnIcePerGame']
                self.games = player_stats['games']
                self.goals_per_game = round(1.0 * self.goals/self.games, 2)

            for injured_player in Player.injured_players:
                if injured_player['player'] == self.full_name:
                    self.injured = True
                    break
            
            logger.debug(f"Obtained {self.full_name} ({self.id})'s stats")

    @staticmethod
    def get_injured_players():
        url = 'https://www.rotowire.com/hockey/tables/injury-report.php?team=ALL&pos=ALL'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError as http_err:
            error_msg = 'HTTP error occured when trying to find list of injured players'
            log_http_error(error_msg, logger, response, http_err)
        else:
            logger.debug('Obtained list of injured players')
            return response.json()

    @staticmethod
    def get_recent_goal_scorers():
        start_date = (datetime.today() - timedelta(days=Player.time_range)).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')
        url = f'https://nhl-score-api.herokuapp.com/api/scores?startDate={start_date}&endDate={end_date}'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError as http_error:
            error_msg = f'HTTP error occured when trying to get recent goal scorers from the past {Player.time_range} days'
            log_http_error(error_msg, logger, response, http_error)
        else:
            goal_scorers = []
            for date in response.json():
                for game in date['games']:
                    if game['status']['state'] == 'FINAL':
                        for goal in game['goals']:
                            goal_scorers.append(goal['scorer']['player'])
            logger.debug('Obtained list of recent goal scorers')
            return Counter(goal_scorers)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.full_name,
            'team': self.team_abbr,
            'position': self.position,
            'goals': self.goals,
            'recent goals': self.recent_goals,
            'goals/game': self.goals_per_game,
            'points': self.points,
            'shots': self.shots,
            'shot %:': self.shot_percentage,
            '+/-:': self.plus_minus,
            'time on ice:': self.time_on_ice,
            'games played': self.games,
            'tims id': self.tims_player_id
        }
    
    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4)

Player.injured_players = Player.get_injured_players()
Player.recent_goal_scorers = Player.get_recent_goal_scorers()
