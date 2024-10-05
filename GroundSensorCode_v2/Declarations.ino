// Import required libraries
#include "WiFi.h"
#include "ESPAsyncWebServer.h"
#include <Adafruit_Sensor.h>
#include <DHT.h>

#define MOISTURE_LEVEL_PIN 32


// Replace with your network credentials
const char* ssid = "Galaxy A52s 5G7F2E";
const char* password = "Frog1453";

#define DHTPIN 33           // Digital pin connected to the DHT sensor
#define DHTTYPE    DHT11    // DHT 22 (AM2302)

/*CLASSES*/
DHT dht(DHTPIN, DHTTYPE);

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);