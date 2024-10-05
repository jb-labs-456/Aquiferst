String readDHTTemperature() {
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  //float t = dht.readTemperature(true);
  // Check if any reads failed and exit early (to try again).
  if (isnan(t)) {    
    Serial.println("Failed to read from DHT sensor!");
    return "--";
  }
  else {
    Serial.println(t);
    return String(t);
  }
}

// Returns moistureRawValue as a normalised value
String readMoisture(void) {
  int moistureValue = analogRead(MOISTURE_LEVEL_PIN);
  int moisturePercent = map(moistureValue, 800, 3500, 100, 0);
  if (moisturePercent > 100) moisturePercent = 100;
  if (moisturePercent < 0) moisturePercent = 0;
  
  Serial.print("Raw Moisture Value: ");
  Serial.print(moistureValue);
  Serial.print(" -> Moisture Percent: ");
  Serial.println(moisturePercent);

  String moisturePercentStr = String(moisturePercent);
  return moisturePercentStr;
}

String readDHTHumidity() {
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  if (isnan(h)) {
    Serial.println("Failed to read from DHT sensor!");
    return "--";
  }
  else {
    Serial.println(h);
    return String(h);
  }
}

// Replaces placeholder with DHT values
String processor(const String& var){
  //Serial.println(var);
  if(var == "TEMPERATURE"){
    return readDHTTemperature();
  }
  else if(var == "HUMIDITY"){
    return readDHTHumidity();
  }
  else if(var == "MOISTURE"){
    return readMoisture();
  }
  return String();
}