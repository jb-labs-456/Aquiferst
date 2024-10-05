import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File path of your local HTML file that contains the sensor readings
file_path = r'C:\Users\miaaz\Downloads\please.html'  # Use a raw string to handle backslashes

def get_float_from_text(soup, sensor_name):
    p_tags = soup.find_all('p')
    for p in p_tags:
        text = p.get_text(strip=True)
        if sensor_name in text:
            # Extract the value after '='
            parts = text.split('=')
            if len(parts) == 2:
                value_str = parts[1].strip()
                try:
                    return float(value_str)
                except ValueError:
                    logger.warning(f"Value for '{sensor_name}' is not a valid float.")
                    return None
    logger.warning(f"Sensor '{sensor_name}' not found in the HTML.")
    return None

def fetch_sensor_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        exit(1)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract sensor readings using the updated function
    nitrogen = get_float_from_text(soup, 'Nitrogen')
    phosphorus = get_float_from_text(soup, 'Phosphorus')
    potassium = get_float_from_text(soup, 'Potassium')
    humidity = get_float_from_text(soup, 'Humidity')
    temperature = get_float_from_text(soup, 'Temperature')
    soil_moisture = get_float_from_text(soup, 'Soil Moisture')  # Note the space

    sensor_values = [nitrogen, phosphorus, potassium, humidity, temperature, soil_moisture]
    if any(value is None for value in sensor_values):
        logger.error("One or more sensor values are missing or invalid.")
        exit(1)
    
    sensor_data = {
        'NPK_levels': {
            'Nitrogen': nitrogen,
            'Phosphorus': phosphorus,
            'Potassium': potassium
        },
        'Humidity': humidity,
        'Temperature': temperature,
        'Soil_Moisture': soil_moisture
    }
    return sensor_data

ideal_thresholds = {
    'NPK_levels': {
        'Nitrogen': (40, 60),
        'Phosphorus': (25, 35),
        'Potassium': (20, 30)
    },
    'Humidity': (50, 75),       # Ideal humidity for crops (%)
    'Temperature': (15, 25),    # Ideal temperature for crops in Celsius
    'Soil_Moisture': (25, 40)   # Ideal soil moisture percentage (%)
}

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

def assess_soil_health(sensor_data, thresholds):
    scores = []
    suggestions = []
    for variable, value in sensor_data.items():
        if isinstance(value, dict):
            # For NPK levels
            for subvar, subval in value.items():
                ideal_min, ideal_max = thresholds[variable][subvar]
                score = compute_score(subval, ideal_min, ideal_max)
                scores.append(score)
                if score < 1.0:
                    if subval < ideal_min:
                        suggestions.append(
                            f"Increase {subvar} level: current {subval}, ideal minimum {ideal_min}."
                        )
                    elif subval > ideal_max:
                        suggestions.append(
                            f"Decrease {subvar} level: current {subval}, ideal maximum {ideal_max}."
                        )
        else:
            # For other variables
            ideal_min, ideal_max = thresholds[variable]
            score = compute_score(value, ideal_min, ideal_max)
            scores.append(score)
            if score < 1.0:
                if value < ideal_min:
                    suggestions.append(
                        f"Increase {variable}: current {value}, ideal minimum {ideal_min}."
                    )
                elif value > ideal_max:
                    suggestions.append(
                        f"Decrease {variable}: current {value}, ideal maximum {ideal_max}."
                    )
    total_score = sum(scores) / len(scores)
    return total_score, suggestions

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
