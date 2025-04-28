from google import genai
from flask import Request
import passwords
api_key = passwords.api_key
def process_request(request: Request):
    """
    Cloud Function to process ECU log data and return extracted parameters.
    """
    request_json = request.get_json(silent=True)
    if not request_json or "file_content" not in request_json:
        return "Invalid request. 'file_content' is required.", 400

    file_content = request_json["file_content"]

    task_prompt = """"# ECU Data Extraction Task

## Background
I need to extract specific vehicle diagnostic parameters from an ECU log file to feed into machine learning models. The log contains various vehicle parameters with timestamps and other metadata, but I only need certain variables formatted in a specific way.

## Your Tasky
Extract the following parameters from the provided ECU log data and return them in a structured format that my code can directly use:

1. ENGINE_POWER (not directly in logs, use ECU voltage as proxy: "ECU voltage" value)
2. ENGINE_COOLANT_TEMP (from "Coolant Temperature" value, without the "°C")
3. ENGINE_LOAD (from "Calculated Load Value" value, remove the "%" sign) 
4. ENGINE_RPM (from "Engine RPM" value, remove the "/min")
5. AIR_INTAKE_TEMP (from "Intake Air Temperature" value, without the "°C")
6. SPEED (from "Vehicle Speed" value, without the "km/h")
7. SHORT TERM FUEL TRIM BANK 1 (from "Short Term Fuel Trim (Bank 1)" value, with "%" removed)
8. THROTTLE_POS (from "Absolute Throttle Position" value, with "%" removed)
9. TROUBLE_CODES (if "Number of Fault Codes" > 0, extract the codes; otherwise use "normal")
10. TIMING_ADVANCE (from "Timing Advance (Cyl. #1)" value, with "°" removed)
11. HOURS (from "Time Since Engine Start" value, without the "h")
12. VIN (from "Vehicle identification number")

## Output Format
Return the data in this exact format - a list of tuples where each tuple contains:
[
    ("ENGINE_POWER", 13.613),
    ("ENGINE_COOLANT_TEMP", 98.0),
    ("ENGINE_LOAD", 32.941177),
    ("ENGINE_RPM", 757.0),
    ("AIR_INTAKE_TEMP", 62.0),
    ("SPEED", 0.0),
    ("SHORT TERM FUEL TRIM BANK 1", 0.78125),
    ("THROTTLE_POS", 16.470589),
    ("TROUBLE_CODES", "normal"),
    ("TIMING_ADVANCE", 9.5),
    ("HOURS", 0.29166666)
    ("VIN", "1HGCM82633A123456")
]

## Critical Requirements
1. Extract ONLY the numeric values - remove all units (%, °C, /min, km/h, etc.)
2. Maintain the exact variable names as shown (including spaces and capitalization)
3. For TROUBLE_CODES, use "normal" if "Number of Fault Codes" = 0.0, otherwise extract the actual trouble codes
4. Convert all values to the appropriate type (float for numeric values, string for TROUBLE_CODES)
5. If a value appears multiple times in the log, use the HIGHEST VALUE found for that parameter
6. Do not add any explanations or comments to your output - just provide the list of tuples

## Example
If the log contains:
2025-04-03,16:58:02.400,FINE,data.ecu,05 Coolant Temperature,98.0 °C
2025-04-03,16:59:02.400,FINE,data.ecu,05 Coolant Temperature,101.5 °C

The corresponding tuple would be:
("ENGINE_COOLANT_TEMP", 101.5)

## Handling Missing Values
If any parameter is missing from the log:
1. DO NOT include a placeholder or default value
2. DO NOT include that parameter in the output
3. Only return the parameters that are explicitly found in the log

Return ONLY the list of tuples with no additional text before or after.

When I said tuple, I meant that, not code output. The output should be a list of tuples, not a dictionary or any other format. The order of the tuples should match the order of the parameters listed above. It should resemble this:

[
    ("ENGINE_POWER", 13.613),
    ("ENGINE_COOLANT_TEMP", 98.0),
    ("ENGINE_LOAD", 32.941177),
    ("ENGINE_RPM", 757.0),
    ("AIR_INTAKE_TEMP", 62.0),
    ("SPEED", 0.0),
    ("SHORT TERM FUEL TRIM BANK 1", 0.78125),
    ("THROTTLE_POS", 16.470589),
    ("TROUBLE_CODES", "normal"),
    ("TIMING_ADVANCE", 9.5),
    ("HOURS", 0.29166666)
    ("VIN", "1HGCM82633A123456")
]

No backticks before or after it.
"""

    task_prompt = f"""{task_prompt}

## Log Data
{file_content}
"""

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=task_prompt
    )

    start_index = response.text.find("[")
    end_index = response.text.rfind("]") + 1
    if start_index == -1 or end_index == -1:
        return "Error: Could not extract the required output.", 500
    return response.text[start_index:end_index], 200
