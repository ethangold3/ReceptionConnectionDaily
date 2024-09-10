import os
import psycopg2
from datetime import date
import random
import networkx as nx

# Get the DATABASE_URL from Heroku's environment variables
DATABASE_URL = os.environ['DATABASE_URL']

# Load the graph
G = nx.read_graphml("data/passing_network.graphml")

def calculate_shortest_path(start_player, end_player):
    try:
        path = nx.shortest_path(G, start_player, end_player)
        return len(path) - 1
    except nx.NetworkXNoPath:
        return None

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
    while True:
        start_player = random.choice(list(G.nodes()))
        start_strength = calculate_cumulative_strength(start_player)
        
        if start_strength >= 5000:
            # Find nodes more than 1 edge away and with strength >= 5000
            potential_end_players = [
                node for node in G.nodes()
                if nx.shortest_path_length(G, start_player, node) > 1
                and calculate_cumulative_strength(node) >= 5000
            ]
            
            if potential_end_players:
                end_player = random.choice(potential_end_players)
                shortest_path_length = nx.shortest_path_length(G, start_player, end_player)
                break
    
    # Insert the new entry
    cursor.execute('''
    INSERT INTO daily_players (date, start_player, end_player)
    VALUES (%s, %s, %s)
    ''', (today, start_player, end_player))
    
    conn.commit()
    print(f"Updated daily players: Date = {today}, Start = {start_player}, End = {end_player}")
    print(f"Shortest path length: {shortest_path_length}")
    print(f"Total strength: {total_strength}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_daily_players()