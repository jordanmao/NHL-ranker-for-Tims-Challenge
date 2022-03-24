import requests
import json


class Player(object):
    def __init__(self, tims_player_data, games_today):
        # NHL player id different from the player id Tim Hortons uses
        self.id = None
        self.tims_player_id = tims_player_data['id']
        self.first_name = tims_player_data['firstName']
        self.last_name = tims_player_data['lastName']
        self.full_name = self.first_name + ' ' + self.last_name
        self.number = tims_player_data['number']
        self.position = tims_player_data['position']
        # NHL team id different from the team id Tim Hortons uses
        self.team_id = None
        self.tims_team_id = tims_player_data['teamId']
        self.goals = 0
        self.points = 0
        self.shots = 0
        self.games = 0
        self.plus_minus = 0
        self.shot_percentage = 0
        self.time_on_ice = 0
        self.goals_per_game = 0

        self.set_nhl_team_id(games_today)
        self.set_nhl_id()
        self.obtain_player_data()

    def set_nhl_team_id(self, games_today):
        # In order to get the player's team NHL ID from its Tim Hortons ID, first we must 
        # obtain the team's abbreviation
        for game in games_today:
            home_team = game['teams']['home']
            away_team = game['teams']['away']
            if home_team['id'] == self.tims_team_id:
                team_abbreviation = home_team['abbr']
                break
            elif away_team['id'] == self.tims_team_id:
                team_abbreviation = away_team['abbr']
                break

        # Obtain list of all the teams in the NHL so we can get their NHL ID
        url = 'https://statsapi.web.nhl.com/api/v1/teams'
        teams = requests.get(url).json()['teams']
        for team in teams:
            if team["abbreviation"] == team_abbreviation:
                self.team_id = team['id']
                return

    def set_nhl_id(self):
        url = f'https://statsapi.web.nhl.com/api/v1/teams/{self.team_id}/roster'
        roster = requests.get(url).json()['roster']
        for player in roster:
            if player['person']['fullName'] == self.full_name:
                self.id = player['person']['id']
                return

    def obtain_player_data(self):
        url = f'https://statsapi.web.nhl.com/api/v1/people/{self.id}/stats?stats=statsSingleSeason&season=20212022'
        player_data = requests.get(url).json()
        if player_data['stats'][0]['splits']:
            player_stats = player_data['stats'][0]['splits'][0]['stat']
            self.goals = player_stats['goals']
            self.points = player_stats['points']
            self.shots = player_stats['shots']
            self.shot_percentage = player_stats['shotPct']
            self.plus_minus = player_stats['plusMinus']
            self.time_on_ice = '00:' + player_stats['timeOnIcePerGame']
            self.games = player_stats['games']
            self.goals_per_game = round(1.0 * self.goals/self.games, 2)

    def json(self):
        return {
            'id': self.id,
            'name': self.full_name,
            'position': self.position,
            'goals': self.goals,
            'goals/game': self.goals_per_game,
            'points': self.points,
            'shots': self.shots,
            'shot %:': self.shot_percentage,
            '+/-:': self.plus_minus,
            'time on ice:': self.time_on_ice,
            'games played': self.games
        }
    
    def print(self):
        print(json.dumps(self.json(), indent=4))