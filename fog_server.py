from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)


THINGSPEAK_API_KEY = os.environ.get("3KEQE9398VZ5NSW1")
THINGSPEAK_URL = "https://api.thingspeak.com/update"

@app.route("/")
def home():
    return "Fog Server is running"

@app.route("/update", methods=["POST"])
def update():
    try:
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

        r = requests.post(THINGSPEAK_URL, data=payload)
        print("ThingSpeak Response:", r.text)

        return jsonify({"status": "forwarded to ThingSpeak"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
