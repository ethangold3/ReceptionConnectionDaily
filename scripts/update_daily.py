import networkx as nx
from datetime import date
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from app.utils import select_daily_players

def update_daily_players():
    graph_path = os.path.join(project_root, "data", "passing_network.graphml")
    daily_players_path = os.path.join(project_root, "data", "daily_players.txt")
    G = nx.read_graphml(graph_path)
    start, end = select_daily_players(G)
    with open(daily_players_path, "w") as f:
        f.write(f"{date.today()}\n{start}\n{end}")
    print(f"Updated daily players: Start = {start}, End = {end}")
    # Verify the shortest path length
    path_length = nx.shortest_path_length(G, start, end)
    print(f"Shortest path length: {path_length}")

if __name__ == "__main__":
    update_daily_players()