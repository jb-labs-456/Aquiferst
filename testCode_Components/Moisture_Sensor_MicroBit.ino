// /*
//   https://www.sgeducation.ie/kitronik-mini-prong-soil-moisture-sensor-for-bbc-microbit
//   Use analogRead(); Intended to run at 3V (though seems to work at 3.3V)


//   Note: To ensure that the mini Prong moisture sensor has a long and fulfilling life, 
//   it is better to write your code to perform a moisture check every so often rather than continuously. 
//   When the check is performed continuously it promotes rapid erosion of the electrodes.
// */

// #define MOISTURE_LEVEL_PIN A1
  
// void setup() { 

//   Serial.begin(9600);
// } 
  
// void loop() { 
   
//   Serial.println(analogRead(MOISTURE_LEVEL_PIN));
//   delay(100);
// }