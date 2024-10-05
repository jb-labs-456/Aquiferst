// int outputPin = 3; // Set the pin to which you want to write the analog value (PWM pin)

// void setup() {
//   Serial.begin(9600);    // Start serial communication at 9600 baud rate
//   pinMode(outputPin, OUTPUT); // Set the specified pin as OUTPUT
// }

// void loop() {
//   if (Serial.available() > 0) {
//     int inputValue = Serial.parseInt(); // Read the number entered in the Serial Monitor
//     if (inputValue >= 0 && inputValue <= 255) {  // Check if the number is within the range 0-255
//       analogWrite(outputPin, inputValue);  // Write the input value to the specified pin
//       Serial.print("Analog value written to pin: ");
//       Serial.println(inputValue);          // Feedback in the Serial Monitor
//     } else {
//       Serial.println("Please enter a number between 0 and 255");
//     }
//   }
// }
