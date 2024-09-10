import random
import networkx as nx

def select_daily_players(G):
    while True:
        # Calculate node strengths (sum of edge weights)
        node_strengths = {node: sum(G[node][neighbor]['weight'] for neighbor in G[node]) for node in G.nodes()}
        
        # Filter start candidates based on strength
        start_candidates = [node for node in G.nodes() if node_strengths[node] >= 5000]
        
        if not start_candidates:
            continue
        
        start_player = random.choice(start_candidates)
        
        # Get all nodes that are exactly 3 steps away from the start_player
        nodes_at_distance_3 = [node for node, distance in nx.single_source_shortest_path_length(G, start_player).items() if distance > 1]
        
        if nodes_at_distance_3:
            # Filter end candidates based on combined strength
            end_candidates = [node for node in nodes_at_distance_3 if node_strengths[node] >= 5000]
            
            if end_candidates:
                end_player = random.choice(end_candidates)
                # Verify that the shortest path is indeed 3
                if nx.shortest_path_length(G, start_player, end_player) >1 :
                    return start_player, end_player

def calculate_score(G, path):
    if len(path) < 2:
        return 0
    
    total_weight = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
    return int(total_weight)


def calculate_best_path(G, start, end):
    try:
        # Create a copy of the graph with non-negative weights
        G_non_negative = G.copy()
        for u, v, data in G_non_negative.edges(data=True):
            data['weight'] = max(0, data['weight'])  # Convert negative weights to zero
        
        path = nx.shortest_path(G_non_negative, start, end, weight='weight')
        total_weight = sum(G_non_negative[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        return int(total_weight)
    except nx.NetworkXNoPath:
        return float('inf')  # Return infinity if no path exists
    except nx.NetworkXError as e:
        print(f"NetworkX error in calculate_best_path: {str(e)}")
        return float('inf')  # Return infinity if there's an error