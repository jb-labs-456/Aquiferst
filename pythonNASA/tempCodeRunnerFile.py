import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File path of your local HTML file that contains the sensor readings
file_path = r'C:\Users\miaaz\Downloads\please.html'  # Use a raw string to handle backslashes

# Function to parse float values from text
def get_float_from_text(soup, sensor_name):
    p_tags = soup.find_all('p')
    for p in p_tags:
        text = p.get_text(strip=True)
        print(f"Parsed text: '{text}'")  # Debugging line to see what's being parsed
        if sensor_name.lower() in text.lower():  # Case-insensitive match
            parts = [part.strip() for part in text.split('=')]  # Split by '=' and strip spaces
            if len(parts) == 2:
                try:
                    return float(parts[1])
                except ValueError:
                    logger.warning(f"Value for '{sensor_name}' is not a valid float.")
                    return None
    logger.warning(f"Sensor '{sensor_name}' not found in the HTML.")
    return None

# Function to read the HTML file and extract sensor data
def fetch_sensor_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        exit(1)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract sensor readings
    nitrogen = get_float_from_text(soup, 'Nitrogen')
    phosphorus = get_float_from_text(soup, 'Phosphorus')
    potassium = get_float_from_text(soup, 'Potassium')
    humidity = get_float_from_text(soup, 'Humidity')
    temperature = get_float_from_text(soup, 'Temperature')
    soil_moisture = get_float_from_text(soup, 'Soil Moisture')

    # Check for missing or invalid values
    sensor_values = [nitrogen, phosphorus, potassium, humidity, temperature, soil_moisture]
    for sensor, value in zip(['Nitrogen', 'Phosphorus', 'Potassium', 'Humidity', 'Temperature', 'Soil Moisture'], sensor_values):
        if value is None:
            logger.warning(f"Value for sensor '{sensor}' is missing or invalid.")
    
    sensor_data = {
        'NPK_levels': {
            'Nitrogen': nitrogen if nitrogen is not None else 0,  # Default to 0 if missing
            'Phosphorus': phosphorus if phosphorus is not None else 0,
            'Potassium': potassium if potassium is not None else 0
        },
        'Humidity': humidity if humidity is not None else 0,
        'Temperature': temperature if temperature is not None else 0,
        'Soil_Moisture': soil_moisture if soil_moisture is not None else 0
    }
    return sensor_data

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
def calculate_nutrient_needed(current_level, ideal_level, soil_mass_kg, nutrient_name):
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
                        amount_needed = calculate_nutrient_needed(subval, ideal_min, soil_mass_kg, subvar)
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
    sensor_data = fetch_sensor_data(file_path)
    total_score, suggestions = assess_soil_health(sensor_data, ideal_thresholds)
    
    logger.info(f"Soil Health Score: {total_score:.2f} out of 1.00")
    if suggestions:
        logger.info("Recommendations to improve soil health:")
        for suggestion in suggestions:
            logger.info(suggestion)
    else:
        logger.info("All conditions are ideal. Keep up the good work!")

if __name__ == "__main__":
    main()
