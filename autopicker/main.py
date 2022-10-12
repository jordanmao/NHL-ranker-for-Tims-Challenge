from tims_app_api import TimsAppAPI
import pandas as pd
import numpy as np
import json
import logging
from utils import *
from player import Player
from pathlib import Path
import os


def tabulate_player_set(player_set, games):
    stats = []
    for player_data in player_set:
        player = Player(player_data, games) # also pulls player stats
        if player.injured:
            print(player.full_name, player.team_abbr, 'is absent')
        else:
            stats.append(player.to_dict())
    return pd.DataFrame(stats)


project_path = Path(__file__).parent.parent

# Logging Config --------------------------------------------------------------------
logger = logging.getLogger()
# set up logging to file which writes DEGUG messages or higher to the file
if not os.path.exists(f'{project_path}/logs'):
    os.makedirs(f'{project_path}/logs')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)-12.12s] [%(levelname)-5.5s] [%(filename)-17.17s:%(lineno)-4d] %(message)s',
    datefmt='%m-%d %H:%M',
    filename=f'{project_path}/logs/autopicker.log',
    filemode='w',
    encoding='utf-8')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

tims_app_api = TimsAppAPI()

# Obtain and store history of correct/incorrect picks from Tim Hortons app into history.json
pick_history = tims_app_api.get_pick_history()
with open(f'{project_path}/logs/history.json', 'w') as outfile:
    json_string = json.dumps(pick_history, indent=4)
    outfile.write(json_string)

# Obtain game schedule and player sets from Tim Hortons app
games_and_player_data = tims_app_api.get_games_and_players()

games = games_and_player_data.get('games')
picks = games_and_player_data.get('picks')

# If picks have already been submitted today, store them into picks.json
if picks != None:
    with open(f'{project_path}/logs/picks.json', 'w') as outfile:
        stored_picks = []
        for i in range(3):
            stored_picks.append({
                'setId': i,
                'player': {
                    'id': picks[i]['player']['id'],
                    'name': picks[i]['player']['firstName'] + ' ' + picks[i]['player']['lastName']
                }
            })
        json_string = json.dumps(stored_picks, indent=4)
        outfile.write(json_string)
    logger.info('Picks have already been locked in\nExiting...')
    exit()

# Extract the 3 player sets to pick a player from each
player_sets = [games_and_player_data.get('sets')[i]['players'] for i in range(3)]

if player_sets[0] == []: 
    # if a player set is empty, then the other sets will also be empty, since every set 
    # must contain at least on player on each team playing that day. This is most likely
    # because all the games have started.
    logger.info('No players to choose from right now\nExiting...')
    exit()

# Form dataframes from the 3 player sets
pd.set_option('display.colheader_justify', 'center')

dfs = []
for i in range(3):
    set_num = i + 1
    print(f'Tabulating player set {set_num}...')
    df = tabulate_player_set(player_sets[i], games)
    # Sort the dataframes by goals, recent goals, then goals/game (all in descending order)
    sorted_df = df.sort_values(
        by=['goals', 'recent goals', 'goals/game'], 
        ascending=[False, False, False])
    sorted_df.index = np.arange(1, len(sorted_df) + 1)
    logger.info(f'\nPlayer set {set_num}\n{sorted_df}\n\n')
    dfs.append(sorted_df)  
    # Export dataframe rankings to excel file
    sorted_df.to_excel(f'{project_path}/logs/rankings_set{set_num}.xlsx', sheet_name='rankings')

# The top row of each of the 3 sorted dataframes represents the 3 players to pick
names_of_picks = [df.iloc[0]['name'] for df in dfs]
tims_ids_of_picks = [df.iloc[0]['tims id'] for df in dfs]

with open(f'{project_path}/logs/picks.json', 'w') as outfile:
    stored_picks = []
    for i in range(3):
        stored_picks.append({
            'setId': i,
            'player': {
                'id': tims_ids_of_picks[i],
                'name': names_of_picks[i]
            }
        })
        logger.info(f"Pick {i+1}. {names_of_picks[i]}, {tims_ids_of_picks[i]}")
    json_string = json.dumps(stored_picks, indent=4)
    outfile.write(json_string)

# Submit 3 picks
tims_app_api.submit_picks(tims_ids_of_picks)
print('\n')
logger.info('Picks submission was successful')