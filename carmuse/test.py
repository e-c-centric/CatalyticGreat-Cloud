import requests
import json

url = "https://us-central1-tidal-discovery-455813-e2.cloudfunctions.net/process_nlp_query"

payload = {
    "phase": 1,
    "question": "How many vehicles in the system have a remaining lifetime of less than 1000 hours?"
}

response = requests.post(url, json=payload)

print("Status code:", response.status_code)
try:
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)