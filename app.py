from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Replace with your API keys and endpoints
WEATHER_API_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
BUS_API_URL = "https://api.entur.io/journey-planner/v2/graphql"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather')
def get_weather():
    params = {"lat": 63.42, "lon": 10.39}  # Trondheim coordinates
    headers = {"User-Agent": "RaspberryPi-Dashboard"}
    response = requests.get(WEATHER_API_URL, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            timeseries = data["properties"]["timeseries"][:5]  # Get next few forecasts
            forecast_data = []
            
            for entry in timeseries:
                time = entry["time"]
                details = entry["data"]["instant"]["details"]
                temperature = details["air_temperature"]
                condition = entry["data"].get("next_1_hours", {}).get("summary", {}).get("symbol_code", "unknown")
                
                forecast_data.append({"time": time, "temperature": temperature, "condition": condition})
            
            return jsonify(forecast_data)
        except KeyError:
            return jsonify({"error": "Could not extract weather data"})
    else:
        return jsonify({"error": "Failed to fetch weather data"}), 500

@app.route('/bus_times')
def get_bus_times():
    stop_place_id = "NSR:StopPlace:60257"  # Lerkendal Stop Place ID
    headers = {
        "Content-Type": "application/json",
        "ET-Client-Name": "RaspberryPi-Dashboard"
    }

    query = {
        "query": f"""
        {{
            stopPlace(id: "{stop_place_id}") {{
                name
                estimatedCalls(timeRange: 7200, numberOfDepartures: 5) {{
                    expectedDepartureTime
                    destinationDisplay {{
                        frontText
                    }}
                    serviceJourney {{
                        journeyPattern {{
                            line {{
                                name
                                transportMode
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
    }

    response = requests.post(BUS_API_URL, json=query, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Raw Response from Entur API:", data)  # Debugging

        try:
            calls = data["data"]["stopPlace"]["estimatedCalls"]
            bus_data = []

            for call in calls:
                time = call["expectedDepartureTime"]
                destination = call["destinationDisplay"]["frontText"]
                line = call["serviceJourney"]["journeyPattern"]["line"]["name"]
                transport_mode = call["serviceJourney"]["journeyPattern"]["line"]["transportMode"]

                bus_data.append({"time": time, "destination": destination, "line": line, "mode": transport_mode})

            print("Processed Bus Data:", bus_data)  # Debugging
            return jsonify(bus_data)
        except KeyError as e:
            print("KeyError:", e)  # Debugging
            return jsonify({"error": "Could not extract bus times"}), 500
    else:
        print("Failed to fetch bus times. Status Code:", response.status_code)  # Debugging
        return jsonify({"error": "Failed to fetch bus times"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
