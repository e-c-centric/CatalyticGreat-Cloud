import requests

# Read the file content
with open(r"refine_func\filtered_data.txt", "r") as file:
    file_content = file.read()

# print(file_content)

# Define the payload
payload = {"file_content": file_content}

# Send the POST request
url = "https://us-central1-tidal-discovery-455813-e2.cloudfunctions.net/process_request"
response = requests.post(url, json=payload)

# Print the response
print(response.text)