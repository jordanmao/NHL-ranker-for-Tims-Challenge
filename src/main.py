from tims_app_interface import TimsAppInterface
from player import Player
import requests
import pandas as pd


def tabulate_player_set(player_set):
    stats = []
    for player_data in player_set:
        player = Player(player_data, games) # also pulls player stats
        stats.append(player.json())
    return pd.DataFrame(stats)
    
# Obtain game schedule and player sets from Tim Hortons app
tims_app_interface = TimsAppInterface()
games_and_player_data = tims_app_interface.get_games_and_players()
print('Obtained game schedule and player sets from Tim Hortons\n')

games = games_and_player_data.get('games')
picks = games_and_player_data.get('picks')
if picks != []:
    print('Picks have already been locked in\nExiting...')
    exit()

# Extract the 3 player sets to pick a player from each
player_sets = [games_and_player_data.get('sets')[i]['players'] for i in range(3)]

if player_sets[0] == []: 
    # if a player set is empty, then the other sets will also be empty, since every set 
    # must contain at least on player on each team playing that day. This is most likely
    # because all the games have started.
    print('No players to choose from right now\nExiting...')
    exit()

# Form dataframes from the 3 player sets
pd.set_option('display.colheader_justify', 'center')

dfs = []
for i in range(3):
    set_num = i + 1
    print(f'Tabulating player set {set_num}...')
    df = tabulate_player_set(player_sets[i])
    # Sort the dataframes by goals, goals/game, then points (all in descending order)
    df.sort_values(
        by=['goals', 'goals/game', 'points'], 
        ascending=[False, False, False], 
        inplace=True)
    print(f'\nPlayer set {set_num}\n', df, '\n\n')
    dfs.append(df)

# The top row of each of the 3 sorted dataframes represents the 3 players to pick
names_of_picks = [df.iloc[0]['name'] for df in dfs]
tims_ids_of_picks = [df.iloc[0]['tims id'] for df in dfs]

print('Picks:')
for i in range(3):
    print(f"{i}. {names_of_picks[i]}, {tims_ids_of_picks[i]}")

status_code = tims_app_interface.submit_picks(tims_ids_of_picks)
if status_code == requests.codes.ok:
    print('\nPicks submission was successful')
else:
    print('\nPicks submission was unsuccessful')