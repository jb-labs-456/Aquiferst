import logging
import requests

# ESP32 web server IP address
esp32_ip = 'http://192.168.177.1'  # Replace with the actual IP address of your ESP32

# Thresholds for ideal sensor values
ideal_thresholds = {
    'NPK_levels': {
        'Nitrogen': (40, 60),      # in mg/kg
        'Phosphorus': (25, 35),    # in mg/kg
        'Potassium': (20, 30)      # in mg/kg
    },
    'Humidity': (50, 75),         # Ideal humidity for crops (%)
    'Temperature': (15, 25),      # Ideal temperature for crops in Celsius
    'Soil_Moisture': (25, 40)     # Ideal soil moisture percentage (%)
}

# Function to fetch sensor data from ESP32
def fetch_sensor_data_from_esp32(esp32_ip):
    sensors = ['temperature', 'humidity', 'moisture']
    sensor_data = {}

    for sensor in sensors:
        try:
            response = requests.get(f"{esp32_ip}/{sensor}", timeout=5)
            response.raise_for_status()
            value = response.text.strip()
            try:
                sensor_data[sensor] = float(value)
            except ValueError:
                print(f"Value for '{sensor}' is not a valid float: '{value}'")
                sensor_data[sensor] = None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {sensor} data from ESP32: {e}")
            sensor_data[sensor] = None

    # Map ESP32 sensor names to expected names in the rest of the code
    sensor_data_formatted = {
        'NPK_levels': {
            'Nitrogen': 50.0,    # Placeholder values since ESP32 doesn't provide NPK
            'Phosphorus': 30.0,
            'Potassium': 25.0
        },
        'Humidity': sensor_data['humidity'] if sensor_data['humidity'] is not None else 0,
        'Temperature': sensor_data['temperature'] if sensor_data['temperature'] is not None else 0,
        'Soil_Moisture': sensor_data['moisture'] if sensor_data['moisture'] is not None else 0
    }

    # Debug print to verify sensor data
    print(f"Sensor Data: {sensor_data_formatted}")
    return sensor_data_formatted

# Function to compute health score for each sensor value
def compute_score(value, ideal_min, ideal_max):
    delta = ideal_max - ideal_min
    min_val = ideal_min - delta
    max_val = ideal_max + delta
    if ideal_min <= value <= ideal_max:
        return 1.0
    elif value < ideal_min:
        if value >= min_val:
            return (value - min_val) / (ideal_min - min_val)
        else:
            return 0.0
    else:  # value > ideal_max
        if value <= max_val:
            return (max_val - value) / (max_val - ideal_max)
        else:
            return 0.0

# Function to calculate water needed if soil moisture is low
def calculate_water_needed(current_moisture, ideal_moisture, soil_volume_m3):
    moisture_deficit = (ideal_moisture - current_moisture) / 100.0  # Convert percentage to decimal
    water_volume_m3 = moisture_deficit * soil_volume_m3
    return water_volume_m3 * 1000  # Convert cubic meters to liters

# Function to calculate fertilizer needed based on nutrient levels
def calculate_nutrient_needed(current_level, ideal_level, soil_mass_kg):
    nutrient_deficit_mg_per_kg = ideal_level - current_level
    total_nutrient_needed_mg = nutrient_deficit_mg_per_kg * soil_mass_kg
    return total_nutrient_needed_mg / 1000.0  # Convert mg to grams

# Main function to assess soil health and provide recommendations
def assess_soil_health(sensor_data, thresholds, soil_volume_m3=1.0):
    soil_bulk_density = 1300  # kg/m^3
    soil_mass_kg = soil_bulk_density * soil_volume_m3
    scores = []
    suggestions = []

    for variable, value in sensor_data.items():
        if isinstance(value, dict):
            for subvar, subval in value.items():
                ideal_min, ideal_max = thresholds[variable][subvar]
                score = compute_score(subval, ideal_min, ideal_max)
                scores.append(score)
                if score < 1.0:
                    if subval < ideal_min:
                        amount_needed = calculate_nutrient_needed(subval, ideal_min, soil_mass_kg)
                        suggestions.append(f"Add {amount_needed:.2f} grams of {subvar} fertilizer to reach the ideal level.")
                    elif subval > ideal_max:
                        suggestions.append(f"Decrease {subvar} level: current {subval}, ideal maximum {ideal_max}.")
        else:
            ideal_min, ideal_max = thresholds[variable]
            score = compute_score(value, ideal_min, ideal_max)
            scores.append(score)
            if score < 1.0:
                if value < ideal_min and variable == 'Soil_Moisture':
                    water_needed = calculate_water_needed(value, ideal_min, soil_volume_m3)
                    suggestions.append(f"Add {water_needed:.2f} liters of water to increase soil moisture.")
                elif value < ideal_min:
                    suggestions.append(f"Increase {variable}: current {value}, ideal minimum {ideal_min}.")
                elif value > ideal_max:
                    suggestions.append(f"Decrease {variable}: current {value}, ideal maximum {ideal_max}.")

    total_score = sum(scores) / len(scores)
    return total_score, suggestions

# Main function to run the script
def main():
    sensor_data = fetch_sensor_data_from_esp32(esp32_ip)
    total_score, suggestions = assess_soil_health(sensor_data, ideal_thresholds)

    print(f"Soil Health Score: {total_score:.2f} out of 1.00")
    if suggestions:
        print("Recommendations to improve soil health:")
        for suggestion in suggestions:
            print(suggestion)
    else:
        print("All conditions are ideal. Keep up the good work!")

if __name__ == "__main__":
    main()
