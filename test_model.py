import requests
import json

# URL of the deployed cloud function
url = "https://us-central1-tidal-discovery-455813-e2.cloudfunctions.net/process_vehicle_data"

# Sample input data (VIN now contains a license plate number, no replacement_year)
input_data = {
    "data": [
        ("VIN", "GR123-24"),  # Example license plate; last two digits '24' -> year 2024
        ("ENGINE_POWER", 120),
        ("ENGINE_COOLANT_TEMP", 90),
        ("ENGINE_LOAD", 75),
        ("ENGINE_RPM", 3000),
        ("AIR_INTAKE_TEMP", 25),
        ("SPEED", 60),
        ("SHORT TERM FUEL TRIM BANK 1", 5),
        ("THROTTLE_POS", 20),
        ("TIMING_ADVANCE", 10)
    ]
}

# Send POST request
response = requests.post(url, json=input_data)

# Print the response
if response.status_code == 200:
    print("Response:")
    print(json.dumps(response.json(), indent=4))
else:
    print(f"Error: {response.status_code}")
    print(response.text)