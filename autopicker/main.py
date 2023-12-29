from tims_app_api_client import TimsAppApiClient
from nhl_api_client import NHLApiClient
from pathlib import Path
from utils.autopicker_utils import *
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import json
import logging
import os
import argparse



def setupLogger(log_path: str) -> logging.Logger:
    logger = logging.getLogger()

    # set up logging to file which writes DEGUG messages or higher to the file
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    for handler in logger.handlers:
        logger.removeHandler(handler)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(name)-12.12s] [%(levelname)-5.5s] [%(filename)-17.17s:%(lineno)-4d] %(message)s',
        datefmt='%m-%d %H:%M',
        filename=f'{log_path}/autopicker.log',
        filemode='w',
        encoding='utf-8')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # set a format which is simpler for console use
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


def main() -> None:
    load_dotenv()
    LOG_PATH = os.getenv('LOG_PATH')
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', help='True or False if calculated picks should be submitted', default=False)
    args = parser.parse_args()
    TEST = args.test

    project_path = Path(__file__).parent.parent

    log_path = LOG_PATH if LOG_PATH is not None else f'{project_path}/logs'
    logger = setupLogger(log_path)

    # GET CONTEST DATA -----------------------------------------------------------------------------
    tims_app_api = TimsAppApiClient()

    # Obtain and store history of correct/incorrect picks from Tim Hortons app into history.json
    pick_history = tims_app_api.get_pick_history()
    with open(f'{log_path}/history.json', 'w') as outfile:
        json_string = json.dumps(pick_history, indent=4)
        outfile.write(json_string)

    # Obtain game schedule and player sets from Tim Hortons app
    games_and_player_data = tims_app_api.get_games_and_players()
    if games_and_player_data.get('code') and games_and_player_data.get('code') == 'noContest':
        logger.info('No contest right now')
        logger.info('Exiting...')
        return

    games = games_and_player_data.get('games')
    picks = games_and_player_data.get('picks')
    sets = games_and_player_data.get('sets')

    # If picks have already been submitted today, store them into picks.json
    if picks != None:
        logger.info('Picks have already been locked in:')
        selected_player_names = [f"{p['player']['firstName']} {p['player']['lastName']}" for p in picks]
        selected_player_ids = [p['player']['id'] for p in picks]
        store_picks(selected_player_names, selected_player_ids, f'{log_path}/picks.json')
        for i in range(3):
            logger.info(f"Pick {i+1}. {selected_player_names[i]}, {selected_player_ids[i]}")
        logger.info('Exiting...')
        return

    # Check if there are any players available for selection
    if sets[0]['players'] == []:
        logger.info('No players left available for selection')
        logger.info('Exiting...')
        return

    # PLAYER AUTO-SELECTION ------------------------------------------------------------------------
    nhl_api_client = NHLApiClient()

    # Load team name mapping fixes (mainly to account for accents, e.g. Montréal Canadiens)
    team_name_fixes_file_name = f'{project_path}/autopicker/data/team_name_fixes.json'
    team_name_fixes = json.load(open(team_name_fixes_file_name, 'r', encoding='utf-8'))

    # Load player jersey number fixes
    jersey_number_fixes_file_name = f'{project_path}/autopicker/data/jersey_number_fixes.json'
    jersey_number_fixes = json.load(open(jersey_number_fixes_file_name, 'r', encoding='utf-8'))

    tims_team_id_to_abbr_map = map_tims_team_id_to_nhl_team_abbr(nhl_api_client, games, team_name_fixes)
    team_abbr_to_roster_map = map_team_abbr_to_roster(nhl_api_client, tims_team_id_to_abbr_map.values())

    # Extract the 3 player sets to pick a player from each
    player_sets = [games_and_player_data.get('sets')[i]['players'] for i in range(3)]

    # Create dataframes from the 3 player sets
    pd.set_option('display.colheader_justify', 'center')

    dfs = []
    for i in range(3):
        set_num = i + 1
        print(f'Tabulating player set {set_num}...')
        df = tabulate_player_set(nhl_api_client, player_sets[i], tims_team_id_to_abbr_map, 
                                team_abbr_to_roster_map, jersey_number_fixes)

        # Sort the dataframes by goals, recent goals, then goals/game (all in descending order)
        sorted_df = df.sort_values(
            by=['goals', 'recent goals', 'goals/game'], 
            ascending=[False, False, False])
        
        sorted_df.index = np.arange(1, len(sorted_df) + 1)
        logger.info(f'\nPlayer set {set_num}\n{sorted_df.to_string()}\n\n')
        dfs.append(sorted_df)

        # Export dataframe rankings to excel file
        sorted_df.to_excel(f'{log_path}/rankings_set{set_num}.xlsx', sheet_name='rankings')

    # The top row of each of the 3 sorted dataframes represents the 3 players to pick
    selected_player_names = [df.iloc[0]['name'] for df in dfs]
    selected_player_ids = [df.iloc[0]['tims id'] for df in dfs]

    store_picks(selected_player_names, selected_player_ids, f'{log_path}/picks.json')
    for i in range(3):
        logger.info(f"Pick {i+1}. {selected_player_names[i]}, {selected_player_ids[i]}")

    if TEST is False:
        # Submit 3 picks
        tims_app_api.submit_picks(selected_player_ids)
        print('\n')
        logger.info('Picks submission was successful')


if __name__ == "__main__":
    main()
