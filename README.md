# 🌱 Smart Plant Monitoring System with Node-RED

## 📌 Overview
ESP32-based system for monitoring and automating plant care. It tracks soil moisture, water levels, rain, temperature, humidity, and light, integrates with Node-RED for real-time dashboard visualization, and supports MQTT for remote monitoring.

## 🔹 Features
- 💧 **Soil & Water Monitoring** – Auto irrigation via MQTT.
- ☔ **Rain Detection** – Alerts during heavy rain.
- 🌡 **Environment Tracking** – Logs temp, humidity, and light.
- 🚨 **Visual & Audio Alerts** – LED & buzzer warnings.
- 📡 **Wi-Fi & MQTT** – Publishes real-time data to Node-RED.
- 📊 **Dashboard Support** – View live plant status with Node-RED.

## 🔧 Components
ESP32, DHT11, Soil & Water Sensors, Rain Sensor, Neopixel LED, OLED (SSD1306), Buzzer, Pump, Light Sensor.

## 🚀 Usage
- Auto-monitors & irrigates.
- Sends MQTT updates for real-time monitoring.
- View live data on Node-RED dashboard.
- Control the water pump remotely via MQTT.
