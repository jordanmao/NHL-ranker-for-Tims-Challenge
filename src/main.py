from tims_app_connector import TimsAppConnector

tims_app_connector = TimsAppConnector()
games_and_player_data = tims_app_connector.getGamesAndPlayers()
games = games_and_player_data.get('games')
player_sets = games_and_player_data.get('sets')
print(games)
print(player_sets)