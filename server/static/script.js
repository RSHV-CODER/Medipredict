const socket = io(); // Connect to Flask-SocketIO server

// Update sensor data dynamically
socket.on("sensor_data", (data) => {
    document.getElementById("heartRate").innerText = data.heart_rate + " BPM";
    document.getElementById("spo2").innerText = data.spo2 + " %";
    document.getElementById("temperature").innerText = data.temperature + " °C";
    document.getElementById("movement").innerText = data.fall_detected ? "🚨 Fall Detected!" : "Normal";
    
    // Update Predicted Disease in Real-Time
    document.getElementById("predictedDisease").innerText = data.prediction;
});

// Handle fall alerts
socket.on("fall_alert", (alertData) => {
    let alertBox = document.getElementById("alertBox");
    alertBox.innerText = alertData.message;
    alertBox.style.display = "block";
    alertBox.style.backgroundColor = "red"; // Highlight the alert
    setTimeout(() => {
        alertBox.style.display = "none";
        alertBox.style.backgroundColor = ""; // Reset after hiding
    }, 5000); // Hide alert after 5 sec
});
