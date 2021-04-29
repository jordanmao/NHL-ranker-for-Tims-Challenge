import json
import requests

class Player(object):
    def __init__(self, player_id, player_name):
        self.player_id = player_id
        self.player_name = player_name
        self.goals = 0
        self.points = 0
        self.shots = 0
        self.shot_percentage = 0
        self.plus_minus = 0
        self.ice_time_per_game = 0
        self.games = 0
        self.obtainPlayerStats()

    def obtainPlayerStats(self):
        link = 'https://statsapi.web.nhl.com/api/v1/people/' + str(self.player_id) + \
               '/stats?stats=statsSingleSeason&season=20202021'
        player_data = requests.get(link).json()
        if player_data['stats'][0]['splits']:
            player_stats = player_data['stats'][0]['splits'][0]['stat']
            self.goals = player_stats['goals']
            self.points = player_stats['points']
            self.shots = player_stats['shots']
            self.shot_percentage = player_stats['shotPct']
            self.plus_minus = player_stats['plusMinus']
            self.ice_time_per_game = player_stats['timeOnIcePerGame']
            self.games = player_stats['games']

    def printPlayerStats(self):
        print('player ID:', self.player_id)
        print('player name:', self.player_name)
        print('goals:', self.goals)
        print('points:', self.points)
        print('shots:', self.shots)
        print('shot %:', self.shot_percentage)
        print('+/-:', self.plus_minus)
        print('ice time per game:', self.ice_time_per_game)
        print('games:', self.games)


class Team(object):
    def __init__(self, team_id, team_name):
        self.team_id = team_id
        self.team_name = team_name
        self.link = 'https://statsapi.web.nhl.com/api/v1/teams/' + str(team_id)
        self.roster = []
        self.obtainRoster()

    def obtainRoster(self):
        roster_data = requests.get('https://statsapi.web.nhl.com/api/v1/teams/' +
                                    str(self.team_id) + '?expand=team.roster').json()
        for player_data in roster_data['teams'][0]['roster']['roster']:
            if player_data['position']['type'] != 'Goalie':
                person = player_data['person']
                self.roster.append(Player(person['id'], person['fullName']))

    def printTeamRoster(self):
        for player in self.roster:
            print(player.player_name)


class TeamsPlaying(object):
    def __init__(self):
        self.teams_list = []
        self.obtainTeamsPlayingList()

    def obtainTeamsPlayingList(self):
        schedule_data = requests.get('https://statsapi.web.nhl.com/api/v1/schedule').json()
        for game in schedule_data['dates'][0]['games']:
            home_team_data = game['teams']['home']['team']
            away_team_data = game['teams']['away']['team']
            home_team = Team(home_team_data['id'], home_team_data['name'])
            away_team = Team(away_team_data['id'], away_team_data['name'])
            self.teams_list.append(home_team)
            self.teams_list.append(away_team)

    def printTeamsPlaying(self):
        for self.team in self.teams_list:
            print(self.team.team_name)


class PlayerList(object):
    def __init__(self, teams):
        self.player_list = []
        self.obtainPlayerList(teams)

    def obtainPlayerList(self, teams):
        for team in teams.teams_list:
            self.player_list += team.roster

    def printPlayerList(self):
        for player in self.player_list:
            print(player.player_id, player.player_name)

    def sortByGoals(self):
        sorted_player_list = self.player_list
        sorted_player_list.sort(key=lambda player: player.goals, reverse=True)
        for rank in range(len(self.player_list)):
            player = self.player_list[rank]
            print('Rank', rank+1, ' Goals:', player.goals,
                  ' Name:', player.player_name, '(' + str(player.player_id) + ')')
        return sorted_player_list

    def sortByPoints(self):
        sorted_player_list = self.player_list
        sorted_player_list.sort(key=lambda player: player.points, reverse=True)
        for rank in range(len(self.player_list)):
            player = self.player_list[rank]
            print('Rank', rank + 1, ' Goals:', player.points,
                  ' Name:', player.player_name, '(' + str(player.player_id) + ')')
        return sorted_player_list



def writeJSONToFile(json_obj, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(json_obj, outfile, indent=4)


teams = TeamsPlaying()

players = PlayerList(teams)
rankedByGoals = players.sortByGoals()
