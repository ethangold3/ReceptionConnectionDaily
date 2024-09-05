from app import app
from flask import render_template, request, jsonify
import networkx as nx
from app.utils import calculate_score
import random
import logging

logging.basicConfig(level=logging.DEBUG)


G = nx.read_graphml("data/passing_network.graphml")



@app.route('/')
def index():
    with open('data/daily_players.txt', 'r') as f:
        date, start_player_id, end_player_id = f.read().splitlines()
    start_player = format_player(start_player_id)
    end_player = format_player(end_player_id)
    return render_template('index.html', start_player=start_player, end_player=end_player, start_player_id=start_player_id, end_player_id=end_player_id)
@app.route('/move', methods=['POST'])
def move():
    data = request.json
    current_player_id = data['current_player']
    next_player_id = data['next_player']
    path_history = data['path_history']
    
    logging.debug(f"Attempting move from {current_player_id} to {next_player_id}")
    
    if current_player_id not in G.nodes:
        logging.error(f"Current player {current_player_id} not in graph")
        return jsonify({'error': 'Current player not found'}), 400
    
    if next_player_id not in G.nodes:
        logging.error(f"Next player {next_player_id} not in graph")
        return jsonify({'error': 'Next player not found'}), 400

    if next_player_id in [item['id'] for item in path_history]:
        logging.error(f"Player {next_player_id} already in path history")
        return jsonify({'error': 'Player already in path'}), 400

    if G.has_edge(current_player_id, next_player_id) or G.has_edge(next_player_id, current_player_id):
        logging.debug(f"Valid move from {current_player_id} to {next_player_id}")
        return jsonify({'success': True, 'next_player': format_player(next_player_id)})
    else:
        logging.debug(f"Invalid move. Finding random 2-step move from {current_player_id}")
        # Random 2-step move
        try:
            path = nx.single_source_shortest_path(G, current_player_id, cutoff=2)
            two_step_players = [p for p in path if len(path[p]) == 3]
            if two_step_players:
                random_next_id = random.choice(two_step_players)
                logging.debug(f"Random 2-step move: {current_player_id} to {random_next_id}")
                return jsonify({
                    'success': False, 
                    'next_player': format_player(random_next_id)
                })
            else:
                logging.debug(f"No 2-step move found. Staying at {current_player_id}")
                return jsonify({
                    'success': False, 
                    'next_player': format_player(current_player_id)
                })
        except nx.NetworkXError as e:
            logging.error(f"NetworkX error: {str(e)}")
            return jsonify({'error': 'Graph error'}), 500

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '').lower()
    matches = []
    for node, data in G.nodes(data=True):
        display_name = data.get('display_name', '')
        if query in display_name.lower():
            matches.append({
                'id': node,
                'formatted': format_player(node)
            })
        if len(matches) == 10:  # Stop after finding 10 matches
            break
    return jsonify(matches)

@app.route('/calculate_score', methods=['POST'])
def calculate_score_route():
    path = request.json['path']
    score = calculate_score(G, path)
    return jsonify({'score': score})


def format_player(player_id):
    node = G.nodes[player_id]
    display_name = node.get('display_name', 'Unknown')
    position = node.get('position', 'Unknown')
    team_abbr = node.get('team_abbr', 'Unknown')
    return f"{display_name} ({position} - {team_abbr})"

def get_player_id(player_name):
    for node, data in G.nodes(data=True):
        if data.get('display_name', '') == player_name:
            return node
    return None