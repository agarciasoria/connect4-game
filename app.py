# connect4_game/app.py
import os
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# This dictionary now holds the entire session, including scores and game settings
session_state = {
    "scores": {},  # e.g., {1: 5, 2: 3}
    "game_config": None, # Will hold {players, connect_n, rows, cols}
    "game": None         # Will hold the board, current_player, etc.
}

PLAYER_COLORS = {1: "Red", 2: "Gold", 3: "Blue", 4: "Green"}

def check_win(player, board, connect_n, rows, cols):
    # Check horizontal
    for r in range(rows):
        for c in range(cols - (connect_n - 1)):
            if all(board[r][c+i] == player for i in range(connect_n)):
                return True
    # Check vertical
    for r in range(rows - (connect_n - 1)):
        for c in range(cols):
            if all(board[r+i][c] == player for i in range(connect_n)):
                return True
    # Check positive diagonal
    for r in range(rows - (connect_n - 1)):
        for c in range(cols - (connect_n - 1)):
            if all(board[r+i][c+i] == player for i in range(connect_n)):
                return True
    # Check negative diagonal
    for r in range(connect_n - 1, rows):
        for c in range(cols - (connect_n - 1)):
            if all(board[r-i][c+i] == player for i in range(connect_n)):
                return True
    return False

def reset_game():
    """Resets the board based on the current configuration."""
    if not session_state["game_config"]:
        return # Can't reset if no game has been configured
    
    config = session_state["game_config"]
    session_state["game"] = {
        "board": [[0] * config["cols"] for _ in range(config["rows"])],
        "current_player": 1,
        "game_over": False,
        "winner": None,
        "message": f"{PLAYER_COLORS[1]}'s Turn"
    }

def get_full_state():
    """Helper to combine all state parts into one object for the frontend."""
    if not session_state["game"]:
        return {"setup_mode": True} # Tell frontend to show setup screen
    
    return {
        "setup_mode": False,
        **session_state["game_config"],
        **session_state["game"],
        "scores": session_state["scores"]
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(get_full_state())

@app.route('/start', methods=['POST'])
def start_game():
    data = request.json
    num_players = int(data.get('players', 2))
    connect_n = int(data.get('connect', 4))

    # Define board sizes based on players (NEW LARGER SIZES)
    if num_players == 2:
        rows, cols = 6, 7   # Classic size
    elif num_players == 3:
        rows, cols = 8, 10  # Larger for 3 players
    else: # 4 players
        rows, cols = 9, 12  # Much larger for 4 players
    
    session_state["game_config"] = {
        "num_players": num_players,
        "connect_n": connect_n,
        "rows": rows,
        "cols": cols
    }
    
    # Initialize scores for the number of players if they don't exist
    for i in range(1, num_players + 1):
        if i not in session_state["scores"]:
            session_state["scores"][i] = 0

    reset_game() # Create the first board
    return jsonify(get_full_state())

@app.route('/move', methods=['POST'])
def move():
    game = session_state["game"]
    config = session_state["game_config"]
    if not game or game["game_over"]:
        return jsonify(get_full_state())

    col = request.json.get('column')
    player = game["current_player"]

    for r in range(config["rows"] - 1, -1, -1):
        if game["board"][r][col] == 0:
            game["board"][r][col] = player
            
            if check_win(player, game["board"], config["connect_n"], config["rows"], config["cols"]):
                game["game_over"] = True
                game["winner"] = player
                game["message"] = f"{PLAYER_COLORS[player]} wins!"
                session_state["scores"][player] += 1
            elif all(game["board"][0][c] != 0 for c in range(config["cols"])): # Draw check
                game["game_over"] = True
                game["message"] = "It's a draw!"
            else:
                game["current_player"] = (player % config["num_players"]) + 1
                game["message"] = f"{PLAYER_COLORS[game['current_player']]}'s Turn"
            
            return jsonify(get_full_state())

    game["message"] = "This column is full! Try another."
    return jsonify(get_full_state())

@app.route('/reset', methods=['POST'])
def reset():
    reset_game()
    return jsonify(get_full_state())

@app.route('/reset_score', methods=['POST'])
def reset_score():
    session_state["scores"] = {}
    # Re-initialize scores for the current number of players
    if session_state["game_config"]:
        num_players = session_state["game_config"]["num_players"]
        for i in range(1, num_players + 1):
            session_state["scores"][i] = 0
    reset_game()
    return jsonify(get_full_state())

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))