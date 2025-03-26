import json
import threading
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO
from ai_model import predict_disease  # AI model for disease prediction
from fall_detection import detect_fall  # Fall detection logic

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket communication

# Store latest sensor data (Thread-Safe)
sensor_data = {
    "heart_rate": 0,
    "spo2": 0,
    "temperature": 0,
    "acceleration": [0, 0, 0],
    "fall_detected": False,
    "prediction": "No Disease Detected"
}
data_lock = threading.Lock()  # Prevents race conditions
#http://192.168.183.18:5000
# ✅ ESP32 Sends Data Here (POST)
@app.route("/post-data", methods=["POST"])
def post_data():
    global sensor_data
    try:
        data = request.get_json()
        
        if not data:
            logging.error("❌ Empty Request Received!")
            return jsonify({"status": "error", "message": "Empty request"}), 400

        # Ensure required fields exist
        required_fields = ["heart_rate", "spo2", "temperature", "acceleration"]
        if not all(k in data for k in required_fields):
            missing_fields = [k for k in required_fields if k not in data]
            logging.error(f"❌ Missing Fields: {missing_fields}")
            return jsonify({"status": "error", "message": f"Missing fields: {missing_fields}"}), 400

        # Validate acceleration format
        if not isinstance(data["acceleration"], list) or len(data["acceleration"]) != 3:
            logging.error("❌ Invalid Acceleration Data!")
            return jsonify({"status": "error", "message": "Invalid acceleration format"}), 400

        # Safely update sensor data
        with data_lock:
            sensor_data.update({
                "heart_rate": float(data["heart_rate"]),
                "spo2": float(data["spo2"]),
                "temperature": float(data["temperature"]),
                "acceleration": data["acceleration"],
                "fall_detected": detect_fall(data["acceleration"])
            })

            # Predict disease using AI model
            sensor_data["prediction"] = predict_disease(sensor_data)

            logging.info(f"📡 Updated Sensor Data: {sensor_data}")

            # Emit updated data to WebSocket clients
            socketio.emit("sensor_data", sensor_data)

            if sensor_data["fall_detected"]:
                socketio.emit("fall_alert", {"message": "⚠️ Fall Detected! Immediate Attention Needed!"})

            socketio.emit("disease_prediction", {"prediction": sensor_data["prediction"]})

        return jsonify({"status": "success", "message": "Data received"}), 200

    except Exception as e:
        logging.error(f"❌ Error Processing Request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

# ✅ Frontend Requests Data Here (GET)
@app.route("/data", methods=["GET"])
def get_data():
    with data_lock:
        return jsonify(sensor_data)  # Send real-time data to frontend

# ✅ Web Dashboard Route for Home Page
@app.route("/")
def home():
    return render_template("index.html")  # Web UI

# ✅ Web Dashboard Route for Dashboard Page
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")  # Web UI


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")
    
# ✅ Dummy Data for Testing (Only if needed)
@app.route("/test", methods=["POST"])
def send_dummy_data():
    global sensor_data
    try:
        dummy_data = {
            "heart_rate": 85,
            "spo2": 97.5,
            "temperature": 36.8,
            "acceleration": [0.1, -0.2, 9.8]  # Simulated stable values
        }
        return post_data()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/firebase.js')
def serve_firebase():
    return send_from_directory("static", "firebase.js", mimetype="application/javascript")

# ✅ Run Flask with WebSocket Support
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
