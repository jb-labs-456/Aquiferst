/*
  The Water Level Sensor uses VCC (5V), GND, and Signal (analog signal 0-5V)
  Simply read the data by analogRead();
  Different readings may occur due to different impurities
*/
#define WATER_LEVEL_PIN A0
  
void setup() { 

  Serial.begin(9600);
} 
  
void loop() { 
   
  Serial.println(analogRead(WATER_LEVEL_PIN));
}