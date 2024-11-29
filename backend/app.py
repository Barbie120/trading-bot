import os
from flask import Flask, jsonify, request, send_from_directory

# Initialize Flask app
app = Flask(__name__, static_folder="static")

# Dummy data for demonstration (replace with actual logic or database integration)
data = {
    "stats": {
        "total_trades": 100,
        "wins": 60,
        "losses": 40,
        "win_rate": 60  # in percentage
    },
    "trades": [
        {"time": "2024-11-28T10:00:00Z", "type": "buy", "profit": 15},
        {"time": "2024-11-28T11:00:00Z", "type": "sell", "profit": -5},
        {"time": "2024-11-28T12:00:00Z", "type": "buy", "profit": 20},
    ]
}

# API endpoint to fetch statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Endpoint to retrieve trading statistics.
    """
    return jsonify(data["stats"])

# API endpoint to fetch trade history
@app.route('/api/trades', methods=['GET'])
def get_trades():
    """
    Endpoint to retrieve trade history.
    Supports filtering by start_date and end_date via query parameters.
    """
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    trades = data["trades"]

    # Apply date filtering if start_date and end_date are provided
    if start_date:
        trades = [trade for trade in trades if trade["time"] >= start_date]
    if end_date:
        trades = [trade for trade in trades if trade["time"] <= end_date]

    return jsonify(trades)

# Serve favicon specifically
@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """
    Route to serve the favicon.
    """
    return send_from_directory(app.static_folder, 'favicon.ico')

# Serve the frontend React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static_files(path):
    """
    Route to serve static files like CSS, JS, etc.
    Defaults to serving index.html for unknown paths.
    """
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# Start the Flask app
if __name__ == "__main__":
    # Use PORT environment variable if available, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
