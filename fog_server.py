from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Secure API Key from Render Environment Variables
THINGSPEAK_API_KEY = os.environ.get("3KEQE9398VZ5NSW1")
THINGSPEAK_URL = "https://api.thingspeak.com/update"

# -----------------------------
# HOME ROUTE
# -----------------------------
@app.route("/")
def home():
    return "Fog Server is running with Validation + Timestamp"

# -----------------------------
# DATA VALIDATION FUNCTION
# -----------------------------
def validate_data(data):
    required_fields = [
        "avg_key_latency",
        "avg_click_interval",
        "pause_time",
        "session_duration",
        "fatigue_score",
        "fatigue_state"
    ]

    # Check missing fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    # Value validation rules
    if not (0 <= data["avg_key_latency"] <= 2000):
        return False, "Invalid key latency"

    if not (0 <= data["avg_click_interval"] <= 3000):
        return False, "Invalid click interval"

    if not (0 <= data["pause_time"] <= 600):
        return False, "Invalid pause time"

    if not (0 < data["session_duration"] <= 3600):
        return False, "Invalid session duration"

    if not (0 <= data["fatigue_score"] <= 5):
        return False, "Invalid fatigue score"

    if data["fatigue_state"] not in [0, 1]:
        return False, "Invalid fatigue state"

    return True, "Valid"

# -----------------------------
# UPDATE ROUTE (EDGE → FOG)
# -----------------------------
@app.route("/update", methods=["POST"])
def update():
    try:
        data = request.json
        print("Received from Edge:", data)

        # Validate incoming data
        is_valid, message = validate_data(data)
        if not is_valid:
            print("Validation Failed:", message)
            return jsonify({"error": message}), 400

        # Server-side timestamp tagging
        server_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        print("Validated. Timestamp added:", server_timestamp)

        # Prepare payload for ThingSpeak
        payload = {
            "api_key": THINGSPEAK_API_KEY,
            "field1": data["avg_key_latency"],
            "field2": data["avg_click_interval"],
            "field3": data["pause_time"],
            "field4": data["session_duration"],
            "field5": data["fatigue_score"],
            "field6": data["fatigue_state"],
            "created_at": server_timestamp  # Trusted fog timestamp
        }

        r = requests.post(THINGSPEAK_URL, data=payload)
        print("ThingSpeak Response:", r.text)

        return jsonify({
            "status": "forwarded to ThingSpeak",
            "timestamp": server_timestamp
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
