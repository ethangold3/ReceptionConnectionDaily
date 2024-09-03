
import nfl_data_py as nfl
import pandas as pd
import os

# Import players
players = nfl.import_players()

# Select required columns
player_info = players[['display_name', 'status', 'gsis_id', 'position', 'team_abbr']]

# Ensure the pbp_data directory exists
os.makedirs('pbp_data', exist_ok=True)

# Save to CSV in the pbp_data folder
player_info.to_csv('pbp_data/player_info.csv', index=False)

print("Player info saved to pbp_data/player_info.csv")