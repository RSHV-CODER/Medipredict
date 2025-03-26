#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <MPU6050.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define WIFI_SSID "Infinix"
#define WIFI_PASSWORD "12345678"
#define SERVER_URL "http://192.168.183.18:5000/post-data"

#define ONE_WIRE_BUS 4  // DS18B20 GPIO
WiFiClient espClient;
MPU6050 mpu;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

bool fallDetected = false;

void setup_wifi() {
    Serial.println("🔗 Connecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    WiFi.setAutoReconnect(true);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Connected!");
        Serial.print("📶 IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n❌ WiFi Connection Failed!");
    }
}

float read_temperature() {
    tempSensor.requestTemperatures();
    float temp = tempSensor.getTempCByIndex(0);
    if (temp == DEVICE_DISCONNECTED_C) {
        Serial.println("❌ Temperature sensor not connected or reading failed!");
        return -1.0;
    }
    return temp;
}

void detect_fall() {
    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);
    float accelX = ax / 16384.0;
    float accelY = ay / 16384.0;
    float accelZ = az / 16384.0;

    if (abs(accelX) > 2.0 || abs(accelY) > 2.0 || abs(accelZ) < 0.3) {
        fallDetected = true;
        Serial.println("⚠ Fall Detected!");
    } else {
        fallDetected = false;
    }
}

// Generate dummy values within the specified range
int get_random_heart_rate() {
    return random(80, 91);  // Heartbeat between 80-90
}

float get_random_spo2() {
    return random(80, 91) + random(0, 100) / 100.0;  // SpO2 between 80-90
}

float get_random_oxygen() {
    return random(90, 99) + random(0, 100) / 100.0;  // Oxygen between 90-98
}

void send_data() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi Disconnected! Attempting to reconnect...");
        setup_wifi();
        return;
    }

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    float temperature = read_temperature();
    if (temperature == -1.0) {
        Serial.println("Skipping data send due to invalid temperature reading.");
        return;
    }

    detect_fall();

    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);
    float accelX = ax / 16384.0;
    float accelY = ay / 16384.0;
    float accelZ = az / 16384.0;

    // Generate dummy data only if temperature > 32°C
    int beatAvg = 0;
    float spo2 = 0;
    float oxygen = 0;
    
    if (temperature > 32.0) {
        beatAvg = get_random_heart_rate();
        spo2 = get_random_spo2();
        oxygen = get_random_oxygen();
    }

    String payload = "{";
    payload += "\"heart_rate\": " + String(beatAvg) + ", ";
    payload += "\"spo2\": " + String(spo2, 2) + ", ";
    payload += "\"oxygen\": " + String(oxygen, 2) + ", ";
    payload += "\"temperature\": " + String(temperature, 2) + ", ";
    payload += "\"acceleration\": [" + String(accelX, 2) + ", " + String(accelY, 2) + ", " + String(accelZ, 2) + "], ";
    payload += "\"fall_detected\": " + String(fallDetected ? "true" : "false");
    payload += "}";

    Serial.println("📡 Sending Data: " + payload);
    int httpResponseCode = http.POST(payload);
    Serial.print("🌍 HTTP Response: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
        Serial.println("✅ Data sent successfully!");
    } else {
        Serial.println("❌ HTTP Request Failed!");
    }
    http.end();
}

void setup() {
    Serial.begin(115200);
    setup_wifi();
    Wire.begin(21, 22);
    
    tempSensor.begin();
    Serial.println("✅ DS18B20 Initialized!");

    mpu.initialize();
    if (!mpu.testConnection()) {
        Serial.println("❌ MPU6050 not found!");
    } else {
        Serial.println("✅ MPU6050 Initialized!");
        mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
    }
    
    randomSeed(analogRead(0)); // Initialize random seed
}

void loop() {
    send_data();
    delay(1000);
}
