import requests
from bs4 import BeautifulSoup

# URL of your website that contains the sensor readings
url = 'http://yourwebsite.com/sensor_readings.html'  # Replace with your actual URL

# Fetch the webpage content
response = requests.get(url)
html_content = response.content

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract sensor readings from the HTML
# Adjust the selectors based on your actual HTML structure

# For example, if your sensor readings are within elements with specific IDs
nitrogen = float(soup.find(id='nitrogen').text)
phosphorus = float(soup.find(id='phosphorus').text)
potassium = float(soup.find(id='potassium').text)
humidity = float(soup.find(id='humidity').text)
temperature = float(soup.find(id='temperature').text)
soil_moisture = float(soup.find(id='soil_moisture').text)

# Build the sensor_data dictionary with the extracted values
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

# Define ideal thresholds for each variable
ideal_thresholds = {
    'NPK_levels': {
        'Nitrogen': (40, 60),
        'Phosphorus': (25, 35),
        'Potassium': (20, 30)
    },
    'Humidity': (50, 75),       # Ideal humidity for crops
    'Temperature': (15, 25),    # Ideal temperature for crops in Celsius
    'Soil_Moisture': (25, 40)   # Ideal soil moisture percentage
}

# Define function to check if sensor values are within the ideal range
def check_sensor_data(sensor_data, thresholds):
    alerts = []
    for variable, value in sensor_data.items():
        if isinstance(value, dict):
            # For NPK levels, which are in a dictionary format
            for subvar, subval in value.items():
                if not thresholds[variable][subvar][0] <= subval <= thresholds[variable][subvar][1]:
                    alerts.append(f"{subvar} level is out of range: {subval} (ideal: {thresholds[variable][subvar]})")
        else:
            # For other variables like humidity, temperature, soil moisture
            if not thresholds[variable][0] <= value <= thresholds[variable][1]:
                alerts.append(f"{variable} is out of range: {value} (ideal: {thresholds[variable]})")
    return alerts

# Run the check on the sensor data
sensor_alerts = check_sensor_data(sensor_data, ideal_thresholds)

# Output alerts if any issues are found
if sensor_alerts:
    print("Alerts:")
    for alert in sensor_alerts:
        print(alert)
else:
    print("All sensor values are within the ideal range.")
