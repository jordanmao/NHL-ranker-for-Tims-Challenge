import json
import requests
from webscraper import *

class Player(object):
    def __init__(self, player_id):
        self.player_id = player_id
        self.player_name = ''
        self.goals = 0
        self.points = 0
        self.shots = 0
        self.games = 0
        self.plus_minus = 0
        self.shot_percentage = 0
        self.ice_time_per_game = 0
        self.goals_per_game = 0
        self.obtainPlayerData()

    def obtainPlayerData(self):
        link = 'https://statsapi.web.nhl.com/api/v1/people/' + str(self.player_id)
        player_info = requests.get(link).json()
        self.player_name = player_info['people'][0]['fullName']
        # More detailed stats:
        stats_link = link + '/stats?stats=statsSingleSeason&season=20202021'
        player_data = requests.get(stats_link).json()
        if player_data['stats'][0]['splits']:
            player_stats = player_data['stats'][0]['splits'][0]['stat']
            self.goals = player_stats['goals']
            self.points = player_stats['points']
            self.shots = player_stats['shots']
            self.shot_percentage = player_stats['shotPct']
            self.plus_minus = player_stats['plusMinus']
            self.ice_time_per_game = player_stats['timeOnIcePerGame']
            self.games = player_stats['games']
            self.goals_per_game = round(1.0 * self.goals/self.games, 2)

    def printPlayerStats(self):
        print('player ID:', self.player_id)
        print('player name:', self.player_name)
        print('goals:', self.goals)
        print('points:', self.points)
        print('shots:', self.shots)
        print('shot %:', self.shot_percentage)
        print('+/-:', self.plus_minus)
        print('ice time per game:', self.ice_time_per_game)
        print('games played:', self.games)


class PlayerList(object):
    def __init__(self, selection_list):
        self.player_list = []
        self.obtainPlayerList(selection_list)

    def obtainPlayerList(self, selection_list):
        for player_id in selection_list:
            self.player_list.append(Player(player_id))

    def sortByGoals(self):
        # Sorting
        sorted_player_list = self.player_list
        sorted_player_list.sort(key=lambda player: player.goals, reverse=True)
        # Printing
        for rank in range(len(sorted_player_list)):
            player = sorted_player_list[rank]
            print('Rank', str(rank+1).zfill(3),
                  ' Goals:', str(player.goals).zfill(2),
                  ' Name:', player.player_name)
        return sorted_player_list

    def sortByPoints(self):
        sorted_player_list = self.player_list
        sorted_player_list.sort(key=lambda player: player.points, reverse=True)
        for rank in range(len(self.player_list)):
            player = self.player_list[rank]
            print('Rank', str(rank+1).zfill(3),
                  ' Points:', str(player.points).zfill(2),
                  ' Name:', player.player_name)
        return sorted_player_list

    def sortByGoalsPerGame(self):
        sorted_player_list = self.player_list
        sorted_player_list.sort(key=lambda player: player.goals_per_game, reverse=True)
        for rank in range(len(self.player_list)):
            player = self.player_list[rank]
            output_goals_per_game = str(player.goals_per_game)
            if len(output_goals_per_game) == 3: # if the G/P only has tenths place,
                output_goals_per_game += '0'      # add a trailing 0
            print('Rank', str(rank+1).zfill(3),
                  ' Goals/Game:', output_goals_per_game,
                  ' Name:', player.player_name)
        return sorted_player_list


def writeJSONToFile(json_obj, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(json_obj, outfile, indent=4)


selection_lists = obtainPlayerSelectionLists()
player_lists = [PlayerList(selection_lists[0]),
                PlayerList(selection_lists[1]),
                PlayerList(selection_lists[2])]

while True:
    keyboard_input = input('Sort by goals[1], points[2], or goals/game[3]: ')
    if keyboard_input == 'q':
        print('Quit')
        break

    print('\n')
    if keyboard_input == '1': # Sort by Goals
        rankings = []
        for i in range(3):
            print('PLAYER SELECTION LIST ' + str(i+1) + ':')
            rankings.append(player_lists[i].sortByGoals())
            print('\n')

    elif keyboard_input == '2': # Sort by Points
        rankings = []
        for i in range(3):
            print('PLAYER SELECTION LIST ' + str(i+1) + ':')
            rankings.append(player_lists[i].sortByPoints())
            print('\n')

    elif keyboard_input == '3': #Sort by Goals/Game
        rankings = []
        for i in range(3):
            print('PLAYER SELECTION LIST ' + str(i+1) + ':')
            rankings.append(player_lists[i].sortByGoalsPerGame())
            print('\n')
    else:
        print('Invalid Input\n')