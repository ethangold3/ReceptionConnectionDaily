import random
import networkx as nx

def select_daily_players(G):
    start_candidates = [node for node, degree in G.degree() if degree > 10]
    start_player = random.choice(start_candidates)
    
    current = start_player
    path_length = random.randint(5, 10)
    for _ in range(path_length):
        neighbors = list(G.neighbors(current))
        if not neighbors:
            break
        current = random.choice(neighbors)
    end_player = current

    return start_player, end_player

def calculate_score(G, path):
    if len(path) < 2:
        return 0
    
    total_weight = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
    return int(total_weight)