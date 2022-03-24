from tims_app_interface import TimsAppInterface
from nhl_stats import Player
import json
import pandas as pd


def tabulate_player_set(player_set):
    stats = []
    for player_data in player_set:
        player = Player(player_data, games)
        stats.append(player.json())
    return pd.DataFrame(stats)
    

tims_app_connector = TimsAppInterface()
games_and_player_data = tims_app_connector.get_games_and_players()
print('Obtained game schedule and player sets from Tim Hortons\n')

games = games_and_player_data.get('games')
picks = games_and_player_data.get('picks')
player_sets = games_and_player_data.get('sets')

player_set1 = player_sets[0]['players']
player_set2 = player_sets[1]['players']
player_set3 = player_sets[2]['players']

print('Tabulating player set 1...')
df1 = tabulate_player_set(player_set1).sort_values(by=['goals'], ascending=False)
print('\n\nPlayer set 1\n', df1, '\n')

print('Tabulating player set 2...')
df2 = tabulate_player_set(player_set2).sort_values(by=['goals'], ascending=False)
print('\n\nPlayer set 2\n', df2, '\n')

print('Tabulating player set 3...')
df3 = tabulate_player_set(player_set3).sort_values(by=['goals'], ascending=False)
print('\n\nPlayer set 3\n', df3, '\n')
