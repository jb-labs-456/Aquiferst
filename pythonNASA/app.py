from flask import Flask, jsonify, send_from_directory
import logging
import os
from sensor_utils import fetch_sensor_data, assess_soil_health  # Import your functions

app = Flask(__name__)

# Ideal thresholds dictionary
ideal_thresholds = {
    'NPK_levels': {
        'Nitrogen': (40, 60),
        'Phosphorus': (25, 35),
        'Potassium': (20, 30)
    },
    'Humidity': (50, 75),
    'Temperature': (15, 25),
    'Soil_Moisture': (25, 40)
}

@app.route('/sensor-data')
def get_sensor_data():
    # Construct the file path relative to the app root
    file_path = os.path.join(app.root_path, 'data', 'please.html')

    # Fetch sensor data using the function defined above
    sensor_data = fetch_sensor_data(file_path)
    total_score, suggestions = assess_soil_health(sensor_data, ideal_thresholds)

    # Return JSON response
    response = {
        'score': total_score,
        'suggestions': suggestions
    }
    return jsonify(response)

# Route to serve the main page
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == "__main__":
    app.run()
