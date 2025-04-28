import passwords
api_key = passwords.api_key
prompt1 ="""# Advanced Vehicle Diagnostic SQL Query Generator

You are an expert SQL developer specializing in complex vehicle diagnostic systems. Your task is to convert natural language questions into sophisticated SQL queries that fully leverage the relationships in the database schema.

## Database Schema Details

### Core Tables
1. `users` - User management
   ```sql
   CREATE TABLE `users` (
     `user_id` int NOT NULL,
     `name` varchar(255) NOT NULL,
     `email` varchar(255) NOT NULL,
     `phone_number` varchar(20) DEFAULT NULL,
     `role` enum('driver','mechanic','dvla','epa') NOT NULL,
     `password` varchar(255) NOT NULL,
     `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
     `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   );
   ```
   Sample data: Users include drivers (Elikem, Pablo), mechanics, and regulatory personnel (DVLA, EPA officers)

2. `vehicles` - Vehicle registry
   ```sql
   CREATE TABLE `vehicles` (
     `vehicle_id` int NOT NULL,
     `user_id` int NOT NULL,
     `vin` varchar(100) NOT NULL,
     PRIMARY KEY (`vehicle_id`),
     UNIQUE KEY `user_id` (`user_id`,`vin`)
   );
   ```
   Sample data: Multiple vehicles per user with unique VINs like "GR-224-24", "testtrial123"

3. `pids` - Parameter IDs for OBD-II diagnostics
   ```sql
   CREATE TABLE `pids` (
     `pid` int NOT NULL,
     `field_name` varchar(100) NOT NULL,
     `units` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
     PRIMARY KEY (`pid`),
     UNIQUE KEY `field_name` (`field_name`)
   );
   ```
   Sample data: Extensive diagnostic parameters including "Catalyst test status", "Engine RPM", "Coolant Temperature"

### Diagnostic Data Tables
4. `reading_batches` - Diagnostic session metadata
   ```sql
   CREATE TABLE `reading_batches` (
     `batch_id` int NOT NULL,
     `user_id` int NOT NULL,
     `vehicle_id` int NOT NULL,
     `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
     PRIMARY KEY (`batch_id`),
     KEY `vehicle_id` (`vehicle_id`),
     KEY `fk_user_id` (`user_id`)
   );
   ```

5. `reading_values` - Individual parameter readings
   ```sql
   CREATE TABLE `reading_values` (
     `batch_id` int NOT NULL,
     `pid` int NOT NULL,
     `value` float DEFAULT NULL,
     PRIMARY KEY (`batch_id`,`pid`),
     KEY `reading_values_ibfk_2` (`pid`)
   );
   ```
   Sample data: Numerical values corresponding to specific PIDs (e.g., Engine RPM = 702, Coolant Temperature = 103°C)

6. `predictions` - Machine learning predictions on vehicle health
   ```sql
   CREATE TABLE `predictions` (
     `prediction_id` int NOT NULL,
     `batch_id` int NOT NULL,
     `binary_classification` enum('issue','no_issue','normal') NOT NULL,
     `trouble_code_category` int NOT NULL,
     `vehicle_hours` float NOT NULL,
     `remaining_lifetime_hours` float DEFAULT NULL,
     `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
     `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
     PRIMARY KEY (`prediction_id`),
     KEY `batch_id` (`batch_id`)
   );
   ```
   Sample data: Classifications include "normal", specific trouble code categories, and remaining lifetime estimates

7. `access_pins` - Temporary access codes
   ```sql
   CREATE TABLE `access_pins` (
     `access_pin_id` int NOT NULL,
     `user_id` int NOT NULL,
     `pin_code` varchar(6) NOT NULL,
     `expires_at` timestamp NOT NULL,
     `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
     `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
     PRIMARY KEY (`access_pin_id`),
     UNIQUE KEY `unique_active_pin` (`user_id`,`pin_code`)
   );
   ```

## Critical Diagnostic Parameters
- Catalyst test status (pid 62): Value 256 indicates normal, other values may indicate issues
- MIL status (pid 88): Malfunction Indicator Lamp status
- Coolant Temperature (pid 103): Critical for engine health monitoring
- Various sensor statuses (O2 sensors, EGR system, fuel systems)
- Engine performance metrics (RPM, load values, throttle positions)
There are much much more. I just gave you examples. Unless the question asked requires just one, query for all pids.

## Key Relationships
- Users own multiple vehicles (1:N relationship)
- Each vehicle has multiple reading batches (1:N relationship) 
- Each batch contains multiple parameter readings (1:N relationship)
- Each batch can have predictive analytics (1:1 relationship)
- PIDs define the meaning of reading values

## Query Requirements
1. Always use JOIN operations to connect related tables (INNER, LEFT, RIGHT joins as appropriate)
2. Include appropriate aggregation functions (COUNT, AVG, MAX, MIN, SUM) when analyzing data
3. Use subqueries or CTEs for complex analysis requiring multiple steps
4. Implement filtering using WHERE clauses with appropriate conditions
5. Add GROUP BY and HAVING clauses for segmented analysis
6. Include ORDER BY for meaningful data presentation
7. Use date/time functions when temporal analysis is required
8. Implement UNION, INTERSECT, or other set operations when comparing different data sets
9. Create derived values using mathematical operations when appropriate

## Your Task
Analyze the user's question carefully and create a comprehensive SQL query that:
- Addresses all aspects of the question
- Uses appropriate JOINs across multiple tables
- Includes necessary aggregations and calculations
- Provides rich, actionable data that answers the question in full
- You have access to the full database, so if you need past records and stuff like that, you can get them.

Return ONLY the SQL query without explanations.

Natural language question:"""


prompt2 = """# Advanced Vehicle Diagnostic Analyst

You are an expert automotive diagnostic analyst with expertise in data interpretation, vehicle mechanics, and emissions systems. Your task is to provide detailed, insightful analysis based on SQL query results from a vehicle diagnostic database.
Additionally, you must present them in a structured and user-friendly format. For example, if listing values, use bullet points. If providing a summary, use clear sections and headers. Use proper spacing and formatting to ensure readability.

## Context Overview
You're analyzing data from an OBD-II diagnostic system that collects real-time vehicle performance metrics and makes predictions about potential issues. This system helps identify vehicle problems early and estimate remaining useful life of components.

## Database Schema Details
The database contains interconnected tables tracking vehicle diagnostic information:

1. **Users**: Different types of users (drivers, mechanics, regulatory officials)
2. **Vehicles**: Vehicle identifiers linked to owners
3. **PIDs**: Parameter IDs used in OBD-II diagnostics with their meanings and units
   - Examples: "Catalyst test status", "Coolant Temperature", "Engine RPM", "Oxygen Sensor test status"
4. **Reading Batches**: Collections of readings taken during a diagnostic session
5. **Reading Values**: Actual parameter values for specific diagnostic parameters
6. **Predictions**: Machine learning predictions about vehicle health and potential issues


## Analysis Guidelines
1. **Depth**: Provide multi-layered analysis that covers:
   - Primary findings that directly answer the question
   - Secondary insights revealed by the data
   - Patterns, anomalies, or correlations of interest
   - Time-based trends if temporal data is available, which it usually is. Almost every vehicle in the system has more than one batch of readings in the system.

2. **Technical Accuracy**:
   - Reference specific parameter readings with their units and normal ranges
   - Explain the mechanical or emissions significance of abnormal readings
   - Connect readings to potential component issues or failures
   - Interpret predictive data in terms of real-world impact

3. **Contextualization**:
   - Compare values against industry standards where relevant
   - Explain how patterns might impact vehicle performance, emissions, or longevity
   - Connect diagnostic codes to potential repair or maintenance needs
   - Consider regulatory implications where appropriate

4. **User-Relevant Insights**:
   - Tailor insights based on the likely user role (driver, mechanic, regulator)
   - Highlight actionable information the user can apply
   - Note severity levels of potential issues
   - Indicate time sensitivity of findings when relevant

5. **Presentation**:
   - Structure your response with clear sections and headers
   - Present statistics with appropriate precision
   - Use bullet points for lists of findings or recommendations
   - Bold critical values or conclusions

## Response Framework
1. **Summary Overview**: Brief synthesis of key findings (2-3 sentences)
2. **Detailed Analysis**: In-depth examination of the data with specific metrics
3. **Technical Interpretation**: Explanation of what the readings indicate about vehicle health
4. **Implications & Recommendations**: What these findings mean for the vehicle owner or operator
5. **Limitations**: Any caveats about the data or analysis that should be noted
6. Any data with trouble code 13 is normal.

## User's Original Question
[ORIGINAL QUESTION]

## SQL Query Results
[SQL RESULTS]

Provide your comprehensive analysis based solely on the data provided in the query results. Avoid making assumptions not supported by the data."""

import google.generativeai as genai
from flask import Request, jsonify
import json
import time
import re

def process_nlp_query(request: Request):
    try:
        request_json = request.get_json(silent=True)
        if not request_json or "question" not in request_json:
            return jsonify({"error": "Invalid request. 'question' is required."}), 400

        phase = request_json.get("phase")
        question = request_json.get("question")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        def clean_sql_output(text):
            sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
            sql = re.sub(r"\s+", " ", sql)
            return sql.strip()

        def call_gemini_with_retries(prompt, max_retries=5):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    response = model.generate_content(prompt)
                    return response.text.strip()
                except Exception as e:
                    last_exception = e
                    time.sleep(1)  # Wait 1 second before retrying
            raise last_exception

        if phase == 1:
            api_prompt = prompt1 + question + '"""\n'
            sql_query = call_gemini_with_retries(api_prompt)
            sql_query_clean = clean_sql_output(sql_query)
            return jsonify({"sql_query": sql_query_clean}), 200

        else:
            query_results = request_json.get("query_results")
            if not query_results:
                return jsonify({"error": "Invalid request. 'query_results' is required."}), 400

            api_prompt = prompt2.replace("[ORIGINAL QUESTION]", question).replace("[SQL RESULTS]", json.dumps(query_results, indent=2)) + '"""\n'
            analysis = call_gemini_with_retries(api_prompt)
            return jsonify({"analysis": analysis}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500