import requests
from requests.exceptions import HTTPError
import json
import logging
from utils.logger_utils import log_http_error
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path
from player import Player
from typing import List, Dict, Any

project_path = Path(__file__).parent.parent

logger = logging.getLogger(__name__)

SEASON='20232024'

class NHLApiClient:
    def __init__(self):
        self.injured_player_names: List[int] = self._get_injured_player_names()
        # self.recent_goal_scorers: Counter = self._get_recent_goal_scorers()
        time_range: int = 5
    
    def get_teams(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get('https://api.nhle.com/stats/rest/en/team')
            response.raise_for_status()
            return response.json()['data']
        except HTTPError as http_err:
            error_msg = f"HTTP error occured when trying to obtain list of NHL teams"
            log_http_error(error_msg, logger, response, http_err)

    def get_team_roster(self, team_abbr: str) -> Dict[str, Any]:
        try:
            response = requests.get(f'https://api-web.nhle.com/v1/roster/{self.team_abbr}/{SEASON}')
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            error_msg = f"HTTP error occured when trying to obtain {team_abbr}'s roster"
            log_http_error(error_msg, logger, response, http_err)

    def populate_player_stats(self, player: Player) -> None:
        try:
            response = requests.get(f'https://api-web.nhle.com/v1/player/{player.id}/landing')
            response.raise_for_status()
            player_data = response.json()
            curr_season_totals = player_data['seasonTotals'][-1]
            if curr_season_totals['season'] != int(SEASON):
                logger.error(f'Unable to pull current {SEASON} season totals for {player.full_name} ({player.id})')
                return
            
            for game in player_data['last5Games']:
                player.recent_goals += game['goals']
            
            player.goals = curr_season_totals['goals']
            player.points = curr_season_totals['points']
            player.shots = curr_season_totals['shots']
            player.shot_percentage = curr_season_totals['shootingPctg']
            player.plus_minus = curr_season_totals['plusMinus']
            m, s = curr_season_totals['toi'].split(':')
            player.time_on_ice = timedelta(minutes=m, seconds=s)
            player.games_played = curr_season_totals['games']
            player.goals_per_game = round(1.0 * player.goals/player.games_played, 2)
            player.injured = player.full_name in self.injured_player_names
            
            logger.debug(f"Obtained {player.full_name} ({player.id})'s stats")
        except HTTPError as http_err:
            error_msg = f"HTTP error occurred when trying to trying to obtain {player.full_name} ({player.id})'s stats"
            log_http_error(error_msg, logger, response, http_err)
            
    def _get_injured_player_names():
        try:
            response = requests.get('https://www.rotowire.com/hockey/tables/injury-report.php?team=ALL&pos=ALL')
            response.raise_for_status()
            logger.debug('Obtained list of injured players')
            return {f"{injured['firstname']} {injured['lastname']}" for injured in response.json()}
        except HTTPError as http_err:
            error_msg = 'HTTP error occured when trying to find list of injured players'
            log_http_error(error_msg, logger, response, http_err)

    def _get_recent_goal_scorers():
        start_date = (datetime.today() - timedelta(days=Player.time_range)).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')
        url = f'https://nhl-score-api.herokuapp.com/api/scores?startDate={start_date}&endDate={end_date}'
        for tries in range(1, 4):
            try:
                response = requests.get(url)
                response.raise_for_status()
                break
            except HTTPError as http_error:
                if tries == 3:
                    error_msg = f'HTTP error occured when trying to get recent goal scorers from the past {Player.time_range} days'
                    log_http_error(error_msg, logger, response, http_error)
        
        goal_scorers = []
        for date in response.json():
            for game in date['games']:
                if game['status']['state'] == 'FINAL':
                    for goal in game['goals']:
                        goal_scorers.append(goal['scorer']['player'])
        logger.debug('Obtained list of recent goal scorers')
        return Counter(goal_scorers)
