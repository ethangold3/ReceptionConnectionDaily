import os
import psycopg2
from datetime import date
import random
import networkx as nx

# Get the DATABASE_URL from Heroku's environment variables
DATABASE_URL = os.environ['DATABASE_URL']

# Load the graph
G = nx.read_graphml("data/passing_network.graphml")

def calculate_cumulative_strength(player):
    return sum(G[player][neighbor]['weight'] for neighbor in G.neighbors(player))

def update_daily_players():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    
    # Delete any existing entry for today
    cursor.execute('DELETE FROM daily_players WHERE date = %s', (today,))
    conn.commit()
    
    # Generate new entry

    max_attempts = 1000  # Limit the number of attempts to find valid players

    if today.month == 9 and today.day == 10:  # September 10th
        start_player = "00-0020531"
        end_player = "00-0034869"
    else:
        for _ in range(max_attempts):
            # Find a start player with strength >= 5000
            strong_nodes = [node for node in G.nodes() if calculate_cumulative_strength(node) >= 2500]
            if not strong_nodes:
                raise Exception("No nodes with cumulative strength >= 5000 found in the graph")
            
            start_player = random.choice(strong_nodes)
            
            # Find nodes more than 1 edge away
            nodes_two_away = set(nx.single_source_shortest_path_length(G, start_player, cutoff=2).keys()) - set(G.neighbors(start_player)) - {start_player}
            
            # Filter nodes with strength >= 5000
            strong_end_nodes = [node for node in nodes_two_away if calculate_cumulative_strength(node) >= 5000]
            
            if strong_end_nodes:
                end_player = random.choice(strong_end_nodes)
                shortest_path_length = nx.shortest_path_length(G, start_player, end_player)
                start_strength = calculate_cumulative_strength(start_player)
                end_strength = calculate_cumulative_strength(end_player)
                total_strength = start_strength + end_strength
                
                if 2 <= shortest_path_length:
                    break

    # Insert the new entry
    cursor.execute('''
    INSERT INTO daily_players (date, start_player, end_player)
    VALUES (%s, %s, %s)
    ''', (today, start_player, end_player))
    
    conn.commit()
    print(f"Updated daily players: Date = {today}, Start = {start_player}, End = {end_player}")
    print(f"Shortest path length: {shortest_path_length}")
    print(f"Start player strength: {start_strength}")
    print(f"End player strength: {end_strength}")
    print(f"Total strength: {total_strength}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_daily_players()