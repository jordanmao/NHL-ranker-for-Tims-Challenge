from nhl_api_client import NHLApiClient
from player import Player
from typing import List, Dict, Any
import logging
import pandas as pd
import json

logger = logging.getLogger(__name__)

def map_tims_team_id_to_nhl_team_abbr(nhl_api_client: NHLApiClient, games: List[Dict[str, Any]], 
                                      team_name_fixes: Dict[str, str]) -> Dict[int, str]:
    all_nhl_teams = nhl_api_client.get_teams()
    team_name_to_abbr_map = {team['fullName'] : team['triCode'] for team in all_nhl_teams}
    tims_team_id_to_abbr_map = {}
    for game in games:
        for team in [game['teams']['home'], game['teams']['away']]:
            team_name = team['city'] + ' ' + team['name']
            if team_name in team_name_fixes:
                team_name = team_name_fixes[team_name]
            
            if team_name not in team_name_to_abbr_map:
                logger.exception(f"Unknown NHL team with name: {team_name}")
            
            tims_team_id_to_abbr_map[team['id']] = team_name_to_abbr_map[team_name]
    
    return tims_team_id_to_abbr_map

def map_team_abbr_to_roster(nhl_api_client: NHLApiClient, team_abbreviations: List[str]) -> Dict[str, Any]:
    team_abbr_to_roster_map = {}
    for team_abbr in team_abbreviations:
        roster = nhl_api_client.get_team_roster(team_abbr)
        # Only consider fowards and defensemen
        team_abbr_to_roster_map[team_abbr] = roster['forwards'] + roster['defensemen']
    
    return team_abbr_to_roster_map

def get_updated_jersey_number(tims_player_data: str, jersey_number_fixes: Dict[str, Dict[str, Any]]) -> int:
    if tims_player_data['id'] in jersey_number_fixes:
        return jersey_number_fixes[tims_player_data['id']]
    return int(tims_player_data['number'])

def tabulate_player_set(nhl_api_client: NHLApiClient, tims_player_set: List[Dict[str, Any]], 
                        tims_team_id_to_abbr_map: Dict[int, str], team_abbr_to_roster_map: Dict[str, Any],
                        jersey_number_fixes: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    stats = []
    for tims_player_data in tims_player_set:
        jersey_number = get_updated_jersey_number(tims_player_data, jersey_number_fixes)
        team_abbr = tims_team_id_to_abbr_map[tims_player_data['teamId']]
        for member in team_abbr_to_roster_map[team_abbr]:
            if int(member['sweaterNumber']) != jersey_number:
                continue
            try:
                player = Player(
                    id=member['id'],
                    tims_player_id=tims_player_data['id'],
                    first_name=tims_player_data['firstName'],
                    last_name=tims_player_data['lastName'],
                    jersey_number=jersey_number,
                    position=tims_player_data['position'],
                    team_abbr=team_abbr
                )
                logger.debug(f'Initialized player class for {player.full_name}')
                nhl_api_client.populate_player_stats(player)
                if player.injured:
                    print(player.full_name, player.team_abbr, 'is absent')
                else:
                    stats.append(player.dict())
                break
            except Exception as e:
                logger.error(f'Failed to initialize player data for {player.full_name} ({player.id})')
                continue
    return pd.DataFrame(stats)

def store_picks(player_names: List[str], player_ids: List[int], path: str) -> None:
    with open(path, 'w') as outfile:
        stored_picks = []
        for i in range(3):
            stored_picks.append({
                'setId': i,
                'player': {
                    'id': player_ids[i],
                    'name': player_names[i]
                }
            })
        json_string = json.dumps(stored_picks, indent=4)
        outfile.write(json_string)
