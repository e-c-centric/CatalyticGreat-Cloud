import requests
import json
import pandas as pd
import joblib
from datetime import datetime
from flask import jsonify
import os
import re
import random

# Load models
binary_model      = joblib.load(os.path.join(os.path.dirname(__file__), "model_funcs/binary_model.sav"))
multi_class_model = joblib.load(os.path.join(os.path.dirname(__file__), "model_funcs/Multi_Classification_Model2.sav"))
regression_model  = joblib.load(os.path.join(os.path.dirname(__file__), "model_funcs/Regression_Hours_Model.sav"))

# Features and throttle severity mapping (lower = more strict)
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
throttle_map = {
    'ENGINE_POWER':                0.1,
    'ENGINE_COOLANT_TEMP':         0.2,
    'ENGINE_LOAD':                 0.3,
    'ENGINE_RPM':                  0.5,
    'AIR_INTAKE_TEMP':             0.6,
    'SPEED':                       0.8,
    'SHORT TERM FUEL TRIM BANK 1': 0.4,
    'THROTTLE_POS':                0.3,
    'TIMING_ADVANCE':              0.2
}

def process_vehicle_data(request):
    try:
        # Parse JSON input
        request_json = request.get_json(silent=True)
        if not request_json:
            return jsonify({"error": "No JSON received"}), 400

        data = request_json.get("data")
        if not data:
            return jsonify({"error": "No input data provided."}), 400
        data_dict = dict(data)

        # Extract & validate VIN/license plate
        license_plate = data_dict.get("VIN")
        if not license_plate or not isinstance(license_plate, str):
            return jsonify({"error": f"License plate missing or not a string: '{license_plate}'"}), 400
        match = re.search(r'(\d{2})\D*$', license_plate)
        if not match:
            return jsonify({"error": f"Could not extract last two digits from '{license_plate}'"}), 400
        model_year = int("20" + match.group(1))

        # Compute vehicle age and weight
        current_year = datetime.now().year
        vehicle_age = current_year - model_year
        age_weight  = 1 + (vehicle_age * 0.05)

        # Build weighted_data and track missing features
        weighted_data = {}
        missing_fields = []
        for f in input_features:
            v = data_dict.get(f)
            if isinstance(v, (int, float)):
                weighted_data[f] = v * age_weight
            else:
                weighted_data[f] = 0.0
                missing_fields.append(f)

        input_df = pd.DataFrame([weighted_data])

        # Get model predictions
        binary_pred    = binary_model.predict(input_df)[0]
        multi_class_out = multi_class_model.predict(input_df)[0]
        regression_out  = regression_model.predict(input_df)[0]

        # Base hours & lifetime
        adjusted_hours    = regression_out * (1 - (vehicle_age * 0.65))
        average_life_hrs  = 4 * 365 * 24
        remaining_lifetime = max(0, average_life_hrs - adjusted_hours)

        # Determine throttle factor & outputs
        if missing_fields:
            throttle_factor = min(throttle_map.get(f, 0.05) for f in missing_fields)
            adjusted_hours    *= throttle_factor
            remaining_lifetime *= throttle_factor
            binary_output = 1
            dtc_code = random.randint(0, 12)
        else:
            throttle_factor = 1.0
            binary_output = binary_pred
            dtc_code = int(multi_class_out)

        # Build response
        response = {
            "BinaryClassification":   "Issue" if binary_output == 1 else "Normal",
            "TroubleCodeCategory":    dtc_code,
            "PredictedHours":         max(0.0, float(adjusted_hours)),
            "RemainingLifetimeHours": float(remaining_lifetime)
        }
        if missing_fields:
            response["warning"] = (
                f"{len(missing_fields)} missing ({', '.join(missing_fields)}); "
                f"throttled by {int(throttle_factor * 100)}%."
            )

        return jsonify(response), 200

    except Exception as e:
        err = {"error": str(e)}
        if 'model_year' in locals():
            err["year"] = model_year
        if 'weighted_data' in locals():
            err["weighted_data"] = weighted_data
        return jsonify(err), 500