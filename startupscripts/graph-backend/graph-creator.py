import os
import networkx as nx
import pandas as pd

def create_graph_from_csvs(directory):
    # Initialize an empty graph
    G = nx.Graph()

    # Read player info
    player_info = pd.read_csv(os.path.join('startupscripts', 'pbp_Data', 'player_info.csv'))
    
    # Remove rows with missing gsis_id
    player_info = player_info.dropna(subset=['gsis_id'])
    
    # If there are still duplicates, keep the first occurrence
    player_info_dict = player_info.drop_duplicates(subset=['gsis_id']).set_index('gsis_id').to_dict('index')

    # Read the pbp data file
    pbp_file_path = os.path.join('startupscripts', 'pbp_Data', '1999-2023_data.csv')
    df = pd.read_csv(pbp_file_path)
    
    # Process each row in the DataFrame
    for _, row in df.iterrows():
        passer_id = row['passer_player_id']
        receiver_id = row['receiver_player_id']
        yards = row['receiving_yards']
        
        # Add nodes for passer and receiver if they don't exist
        for player_id in [passer_id, receiver_id]:
            if not G.has_node(player_id):
                player_data = player_info_dict.get(player_id, {})
                G.add_node(player_id, **player_data)
        
        # Add or update edge between passer and receiver
        if G.has_edge(passer_id, receiver_id):
            G[passer_id][receiver_id]['weight'] += yards
        else:
            G.add_edge(passer_id, receiver_id, weight=yards)

    return G

# Directory containing the CSV files
csv_directory = 'pbp_data'

# Create the graph
graph = create_graph_from_csvs(csv_directory)

# Print some basic information about the graph
print(f"Number of nodes: {graph.number_of_nodes()}")
print(f"Number of edges: {graph.number_of_edges()}")

# Save the graph to a file in the current directory
output_file = "passing_network.graphml"
nx.write_graphml(graph, output_file)
print(f"Graph saved to {output_file}")