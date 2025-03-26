from flask import Flask, request, jsonify
from ai_model import predict_disease  # AI model for disease prediction
from fall_detection import detect_fall  # Fall detection algorithm
from alert_system import send_alert  # Alert system for fall notifications

app = Flask(__name__)

# Store latest sensor data
sensor_data = {
    "heart_rate": 0,
    "spo2": 0,
    "temperature": 0,
    "acceleration": [0, 0, 0],
    "fall_detected": False,
    "prediction": "No Disease Detected"
}

@app.route("/data", methods=["POST"])
def receive_sensor_data():
    global sensor_data
    
    try:
        data = request.json  # Receive JSON payload
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Update sensor values
        if "heart_rate" in data:
            sensor_data["heart_rate"] = float(data["heart_rate"])
        if "spo2" in data:
            sensor_data["spo2"] = float(data["spo2"])
        if "temperature" in data:
            sensor_data["temperature"] = float(data["temperature"])
        if "acceleration" in data:
            sensor_data["acceleration"] = data["acceleration"]
            sensor_data["fall_detected"] = detect_fall(data["acceleration"])
        if "fall_detected" in data:
            sensor_data["fall_detected"] = data["fall_detected"]
        
        # Run AI model for disease prediction
        sensor_data["prediction"] = predict_disease(sensor_data)
        
        # If a fall is detected, trigger an alert
        if sensor_data["fall_detected"]:
            send_alert("Fall detected! Immediate attention needed.")
        
        return jsonify({"message": "Data received successfully", "updated_data": sensor_data}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/data", methods=["GET"])
def get_sensor_data():
    return jsonify(sensor_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
