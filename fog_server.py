from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

THINGSPEAK_API_KEY = os.environ.get("THINGSPEAK_API_KEY")
THINGSPEAK_URL = "https://api.thingspeak.com/update"

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    print("Received from Edge:", data)

    payload = {
        "api_key": THINGSPEAK_API_KEY,
        "field1": data["avg_key_latency"],
        "field2": data["avg_click_interval"],
        "field3": data["pause_time"],
        "field4": data["session_duration"],
        "field5": data["fatigue_score"],
        "field6": data["fatigue_state"]
    }

    requests.post(THINGSPEAK_URL, data=payload)
    return jsonify({"status": "forwarded to ThingSpeak"})

@app.route("/")
def home():
    return "Fog Server is running"

if __name__ == "__main__":
    app.run()
