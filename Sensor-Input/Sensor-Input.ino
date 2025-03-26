#include <Wire.h>
#include "MMA845XQ.h"  // Custom accelerometer library

#define BUTTON 3  // Button connected to pin 3

MMA845XQ accel;

float ax, ay, az;
volatile bool state = false;  // Volatile because it's modified in ISR
unsigned long lastDebounceTime = 0;  
const unsigned long debounceDelay = 200;  // Debounce delay in ms

void setup() {
  Serial.begin(9600);
  accel.begin(0x1C);
  accel.begin(true, 16);
  
  pinMode(BUTTON, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUTTON), toggleState, FALLING);
}

void loop() {
  if (state) {
    accel.update();
    ax = accel.getX();
    ay = accel.getY();
    az = accel.getZ();

    // Send data in CSV format for easier parsing in Python
    Serial.print(ax, 6); Serial.print(",");  
    Serial.print(ay, 6); Serial.print(",");
    Serial.println(az, 6);
  }
}

// Improved ISR for button press
void toggleState() {
  if (millis() - lastDebounceTime > debounceDelay) {  // Debounce check
    state = !state;
    Serial.println(state ? "START" : "END");
    lastDebounceTime = millis();
  }
}
