import requests
import json
import pandas as pd
import joblib
from datetime import datetime
from flask import jsonify
import os
import re

# Load models
import os

# Load models
binary_model = joblib.load(os.path.join(os.path.dirname(__file__), "model_funcs/binary_model.sav"))
multi_class_model = joblib.load(os.path.join(os.path.dirname(__file__), "model_funcs/Multi_Classification_Model2.sav"))
regression_model = joblib.load(os.path.join(os.path.dirname(__file__), "model_funcs/Regression_Hours_Model.sav"))

# Define input features
input_features = [
    'ENGINE_POWER',
    'ENGINE_COOLANT_TEMP',
    'ENGINE_LOAD',
    'ENGINE_RPM',
    'AIR_INTAKE_TEMP',
    'SPEED',
    'SHORT TERM FUEL TRIM BANK 1',
    'THROTTLE_POS',
    'TIMING_ADVANCE'
]

# ...existing code...
def process_vehicle_data(request):
    try:
        # Parse JSON input
        request_json = request.get_json()
        # Debug: Show raw request JSON
        print("DEBUG: request_json =", request_json)
        if not request_json:
            return jsonify({"error": "No JSON received"}), 400

        data = request_json.get("data")
        # Debug: Show data after extraction
        print("DEBUG: data =", data)
        if not data:
            return jsonify({"error": "No input data provided."}), 400

        data_dict = dict(data)
        # Debug: Show data_dict
        print("DEBUG: data_dict =", data_dict)
        # Or return it for debugging:
        # return jsonify({"debug_data_dict": data_dict}), 200

        license_plate = data_dict.get("VIN")
        print("DEBUG: license_plate =", license_plate)
        if not license_plate or not isinstance(license_plate, str):
            return jsonify({"error": f"License plate is missing or not a string: '{license_plate}'"}), 400

        match = re.search(r'(\d{2})\D*$', license_plate)
        print("DEBUG: regex match =", match)
        if not match:
            return jsonify({"error": f"Could not extract last two digits from license plate '{license_plate}'"}), 400
        last_two_digits = match.group(1)
        print("DEBUG: last_two_digits =", last_two_digits)
        model_year = int("20" + last_two_digits)
        print("DEBUG: model_year =", model_year)


        # Calculate vehicle age
        current_year = datetime.now().year
        vehicle_age = current_year - model_year

        # Apply aggressive age-based weighting to all numeric features
        age_weight = 1 + (vehicle_age * 0.05)  # Example: 5% weight increase per year
        weighted_data = {
            key: value * age_weight
            for key, value in data_dict.items()
            if isinstance(value, (int, float)) and key in input_features  # Only include expected features
        }

        # Convert weighted data to a DataFrame
        input_df = pd.DataFrame([weighted_data])

        # Ensure all required features are present
        missing_features = [feature for feature in input_features if feature not in weighted_data]
        if missing_features:
            return jsonify({"error": f"Missing input features: {missing_features}"}), 400

        # Binary classification
        binary_output = binary_model.predict(input_df)[0]

        # Multi-class classification
        multi_class_output = multi_class_model.predict(input_df)[0]

        # Regression prediction
        regression_output = regression_model.predict(input_df)[0]

        # Adjust PredictedHours based on vehicle age
        adjusted_hours = regression_output * (1 - (vehicle_age * 0.05))

        # Calculate remaining lifetime of the catalytic converter
        average_lifetime_hours = 5 * 365 * 24  # 8.5 years in hours
        remaining_lifetime = max(0, average_lifetime_hours - adjusted_hours)

        # Return results
        return jsonify({
            "BinaryClassification": "Issue" if binary_output == 1 else "Normal",
            "TroubleCodeCategory": int(multi_class_output),
            "PredictedHours": max(0, float(adjusted_hours)),  # Ensure hours are non-negative
            "RemainingLifetimeHours": float(remaining_lifetime)  # Remaining lifetime in hours
        }), 200

    except Exception as e:
        # Only include variables if they exist
        error_response = {"error": str(e)}
        if 'model_year' in locals():
            error_response["year"] = model_year
        if 'weighted_data' in locals():
            error_response["weighted_data"] = weighted_data
        return jsonify(error_response), 500
# ...existing code...