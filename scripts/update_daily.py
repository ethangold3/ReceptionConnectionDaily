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
        end_player = random.choice(list(G.nodes()))
        
        if start_player != end_player:
            shortest_path_length = calculate_shortest_path(start_player, end_player)
            start_strength = calculate_cumulative_strength(start_player)
            end_strength = calculate_cumulative_strength(end_player)
            total_strength = start_strength + end_strength
            
            if (shortest_path_length and 
                shortest_path_length > 1 and 
                3 <= shortest_path_length <= 6 and 
                total_strength >= 5000):
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