from flask import Flask, jsonify, send_from_directory
import os

# Initialize Flask app
app = Flask(__name__)

# Static folder configuration
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Sample data for statistics and trade history
data = {
    "stats": {
        "total_trades": 3,
        "wins": 2,
        "losses": 1,
        "win_rate": round(2 / 3 * 100, 2)  # Calculate win rate
    },
    "trades": [
        {"time": "2024-11-28T10:00:00Z", "type": "buy", "profit": 15},
        {"time": "2024-11-28T11:00:00Z", "type": "sell", "profit": -5},
        {"time": "2024-11-28T12:00:00Z", "type": "buy", "profit": 20}
    ]
}

# Route to fetch statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Endpoint to get trading statistics
    """
    return jsonify(data["stats"])

# Route to fetch trade history
@app.route('/api/trades', methods=['GET'])
def get_trades():
    """
    Endpoint to get trade history
    """
    return jsonify(data["trades"])

# Serve static files like CSS, JS, and favicon
@app.route('/<path:path>', methods=['GET'])
def serve_static_files(path):
    """
    Route to serve static files from the 'static' directory.
    Defaults to serving 'index.html' if no specific file is requested.
    """
    static_folder = os.path.join(app.root_path, 'static')
    if os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')

# Serve the root route for the frontend
@app.route('/', methods=['GET'])
def serve_root():
    """
    Route to serve the main index.html at the root URL
    """
    return send_from_directory(app.static_folder, 'index.html')

# Serve favicon specifically
@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """
    Route to serve the favicon
    """
    return send_from_directory(app.static_folder, 'favicon.ico')

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)
