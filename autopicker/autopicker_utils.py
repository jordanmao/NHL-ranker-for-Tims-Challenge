
from player import Player
import pandas as pd
import json


def tabulate_player_set(player_set, games, logger):
    stats = []
    for player_data in player_set:
        try:
            print(player_data)
            player = Player(player_data, games) # also pulls player stats
        except Exception as e:
            logger.error('Failed to initialize player data for ' + player_data['firstName'] + " " + player_data['lastName'])
            continue
        if player.injured:
            print(player.full_name, player.team_abbr, 'is absent')
        else:
            stats.append(player.to_dict())
    return pd.DataFrame(stats)

def store_picks(player_names, player_ids, path):
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