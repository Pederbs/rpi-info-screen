from flask import Flask, render_template, jsonify
import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

app = Flask(__name__)

# Replace with your API keys and endpoints
WEATHER_API_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
BUS_API_URL = "https://api.entur.io/journey-planner/v2/graphql"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather')
def get_weather():
    params = {"lat": 63.41060956725268, "lon": 10.396388355277308}  # Trondheim coordinates
    headers = {"User-Agent": "RaspberryPi-Dashboard"}
    response = requests.get(WEATHER_API_URL, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            timeseries = data["properties"]["timeseries"]
            hourly_data = []
            daily_data = {}
            
            now = datetime.now(ZoneInfo("Europe/Oslo"))
            next_24h = now + timedelta(hours=24)
            
            for entry in timeseries:
                time_str = entry["time"]
                forecast_time = datetime.fromisoformat(time_str.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Oslo"))
                # Collect hourly forecast for the next 24 hours
                if now <= forecast_time < next_24h:
                    details = entry["data"]["instant"]["details"]
                    temperature = details["air_temperature"]
                    condition = entry["data"].get("next_1_hours", {}).get("summary", {}).get("symbol_code", "unknown")
                    hourly_data.append({
                        "time": time_str,
                        "temperature": temperature,
                        "condition": condition
                    })
                # Group forecasts by day for the next 7 days
                if forecast_time >= now:
                    day_str = forecast_time.date().isoformat()  # e.g., "2025-03-18"
                    if day_str not in daily_data:
                        daily_data[day_str] = []
                    daily_data[day_str].append({
                        "time": time_str,
                        "forecast_time": forecast_time,
                        "temperature": entry["data"]["instant"]["details"]["air_temperature"],
                        "condition": entry["data"].get("next_1_hours", {}).get("summary", {}).get("symbol_code", "unknown")
                    })
            
            # For each day, select the forecast closest to 12:00 local time
            daily_result = []
            target_hour = 12
            for day, forecasts in daily_data.items():
                best = min(forecasts, key=lambda f: abs(f["forecast_time"].hour - target_hour))
                daily_result.append({
                    "day": day,
                    "temperature": best["temperature"],
                    "condition": best["condition"]
                })
            daily_result.sort(key=lambda x: x["day"])
            daily_result = daily_result[:7]
            hourly_data.sort(key=lambda x: x["time"])
            
            return jsonify({"hourly": hourly_data, "daily": daily_result})
        except KeyError:
            return jsonify({"error": "Could not extract weather data"})
    else:
        return jsonify({"error": "Failed to fetch weather data"}), 500

# (Your /bus_times endpoint remains unchanged)
@app.route('/bus_times')
def get_bus_times():
    url = "https://api.entur.io/journey-planner/v3/graphql"
    headers = {
        "Content-Type": "application/json",
        "ET-Client-Name": "Familien-rpi-infoscreen"
    }
    query = """
    {
    stopPlace(id: "NSR:StopPlace:60257") {
        id
        name
        estimatedCalls(timeRange: 72100, numberOfDepartures: 10) {     
        realtime
        aimedArrivalTime
        aimedDepartureTime
        expectedArrivalTime
        expectedDepartureTime
        actualArrivalTime
        actualDepartureTime
        date
        forBoarding
        forAlighting
        destinationDisplay {
            frontText
        }
        quay {
            id
        }
        serviceJourney {
            journeyPattern {
            line {
                id
                name
                transportMode
            }
            }
        }
        }
    }
    }
    """
    payload = {"query": query}
    response = requests.post(url, headers=headers, json=payload)        
    if response.status_code == 200:
        data = response.json()
        try:
            calls = data["data"]["stopPlace"]["estimatedCalls"]
            bus_data = []
            for call in calls:
                time = call["expectedDepartureTime"]
                destination = call["destinationDisplay"]["frontText"]
                line = call["serviceJourney"]["journeyPattern"]["line"]["id"][11:] + " " + call["destinationDisplay"]["frontText"]
                transport_mode = call["serviceJourney"]["journeyPattern"]["line"]["transportMode"]
                bus_data.append({"time": time, "destination": destination, "line": line, "mode": transport_mode})
            return jsonify(bus_data)
        except KeyError as e:
            print("KeyError:", e)
            return jsonify({"error": "Could not extract bus times"}), 500
    else:
        print("Failed to fetch bus times. Status Code:", response.status_code)
        return jsonify({"error": "Failed to fetch bus times"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
