import random
import networkx as nx

def select_daily_players(G):
    while True:
        start_candidates = [node for node, degree in G.degree() if degree > 50]
        start_player = random.choice(start_candidates)
        
        # Get all nodes that are exactly 5 steps away from the start_player
        nodes_at_distance_5 = [node for node, distance in nx.single_source_shortest_path_length(G, start_player).items() if distance == 4]
        
        if nodes_at_distance_5:
            end_player = random.choice(nodes_at_distance_5)
            # Verify that the shortest path is indeed 5
            if nx.shortest_path_length(G, start_player, end_player) == 4:
                return start_player, end_player

def calculate_score(G, path):
    if len(path) < 2:
        return 0
    
    total_weight = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
    return int(total_weight)