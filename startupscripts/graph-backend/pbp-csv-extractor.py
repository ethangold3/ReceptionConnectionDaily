import nfl_data_py as nfl
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# print(list(nfl.see_pbp_cols()))

needed_columns = [
    'passer_player_id', 'passer_player_name',
    'receiver_player_id', 'receiver_player_name', 'receiving_yards',
]
years = [year for year in range(1999, 2024)]
pbp_df = nfl.import_pbp_data(columns=needed_columns, years=years)
filtered_pbp_df = pbp_df[needed_columns]

# Filter out rows where passer_player_name or receiver_player_name is None or NaN
pbp_df_no_na = filtered_pbp_df.dropna(subset=['passer_player_name', 'receiver_player_name', 'receiving_yards'])

# Create the directory if it doesn't existc
import os
os.makedirs('pbp_Data', exist_ok=True)

# Save the dataframe to a CSV file
pbp_df_no_na.to_csv('pbp_Data/1999-2023_data.csv', index=False)

print(pbp_df_no_na.sort_values('receiving_yards', ascending=True).head())



#cool things
#4th down stuff
# play clock/pace stuff, drive_real_start_time,  'drive_play_count', 'drive_time_of_possession', 'drive_first_downs', 'drive_game_clock_start', 'drive_game_clock_end'
# play_type_nfl
#series_result
#spread_line + total_line over time

# df = nfl.import_ngs_data(stat_type='receiving', years=[2023])