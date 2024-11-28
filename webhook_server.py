from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    # Log or process the incoming alert
    print("Received data:", json.dumps(data))
    if 'action' in data:
        # Here, communicate with your worker bot (e.g., save data, or signal worker in another way)
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
