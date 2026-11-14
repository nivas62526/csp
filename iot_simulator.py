"""
Smart Poultry Farm - ESP32 / IoT Hardware Simulator
Demonstrates how an ESP32 microcontroller or edge gateway posts telemetry to the backend API:
POST /api/iot/telemetry
"""

import sys
import time
import random
import urllib.request
import json

BASE_URL = "http://localhost:5000/api/iot/telemetry"

def send_telemetry(shed_id=1, temperature=28.0, humidity=60.0, ammonia_ppm=10.0, water_level_pct=85.0, feed_level_pct=75.0):
    payload = {
        "shed_id": shed_id,
        "temperature": temperature,
        "humidity": humidity,
        "ammonia_ppm": ammonia_ppm,
        "water_level_pct": water_level_pct,
        "feed_level_pct": feed_level_pct,
        "device_id": "ESP32-NODE-FARM-01"
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            result = json.loads(res_body)
            print(f"[IoT ESP32] Telemetry Sent: Temp={temperature}C, Hum={humidity}%, NH3={ammonia_ppm}ppm, Water={water_level_pct}%")
            if result.get("alerts_triggered"):
                print(f"  🚨 ALERTS TRIGGERED: {result['alerts_triggered']}")
            return result
    except Exception as e:
        print(f"[IoT ESP32 Error] Failed to connect: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("  🐔 SMART POULTRY FARM - ESP32 IOT SENSOR SIMULATOR")
    print("=" * 60)
    print("1. Send Normal Environmental Telemetry (26.5°C, 62% Hum)")
    print("2. Simulate High Temperature Alert (35.2°C > 34°C limit)")
    print("3. Simulate Low Water Tank Alert (15.0% < 20% limit)")
    print("4. Simulate Hazardous Ammonia Gas (28.5 ppm > 25 ppm limit)")
    print("=" * 60)

    # By default, send a healthy reading for Shed 1
    shed = 1
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "1"

    if mode == "2":
        print("Simulating HIGH TEMPERATURE scenario...")
        send_telemetry(shed_id=shed, temperature=35.5, humidity=65.0, ammonia_ppm=12.0, water_level_pct=80.0, feed_level_pct=70.0)
    elif mode == "3":
        print("Simulating LOW WATER TANK scenario...")
        send_telemetry(shed_id=shed, temperature=27.0, humidity=58.0, ammonia_ppm=10.0, water_level_pct=14.0, feed_level_pct=70.0)
    elif mode == "4":
        print("Simulating HAZARDOUS AMMONIA scenario...")
        send_telemetry(shed_id=shed, temperature=28.0, humidity=75.0, ammonia_ppm=29.0, water_level_pct=75.0, feed_level_pct=65.0)
    else:
        print("Simulating NORMAL standard readings...")
        send_telemetry(shed_id=shed, temperature=26.5, humidity=62.0, ammonia_ppm=11.0, water_level_pct=88.0, feed_level_pct=82.0)
