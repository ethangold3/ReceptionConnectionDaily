import networkx as nx
from datetime import date
import sys
import os
import sqlite3

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from app.utils import select_daily_players

db_path = os.path.join(project_root, "data", "daily_players.db")

def update_daily_players():
    graph_path = os.path.join(project_root, "data", "passing_network.graphml")
    G = nx.read_graphml(graph_path)
    start, end = select_daily_players(G)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    cursor.execute('''
    INSERT OR REPLACE INTO daily_players (date, start_player, end_player)
    VALUES (?, ?, ?)
    ''', (today, start, end))
    
    conn.commit()
    conn.close()
    
    print(f"Updated daily players: Date = {today}, Start = {start}, End = {end}")
    # Verify the shortest path length
    path_length = nx.shortest_path_length(G, start, end)
    print(f"Shortest path length: {path_length}")

if __name__ == "__main__":
    update_daily_players()