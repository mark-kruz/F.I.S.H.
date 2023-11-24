#include "header.h"

void setup() {
  initElectronics();
  Serial.begin(115200);
  fishTransfer.begin(Serial); //initialize servos, power on fish servo power rail, open serial transfer to backend
}

void initElectronics() {
  pinMode(PowerFetPin, OUTPUT);
  pinMode(EyeLEDPin, OUTPUT); //pin config as output
  servoInit(mouth,  MouthServoPin, 1000);
  servoInit(body, BodyServoPin, 1000);
  servoInit(tail, TailServoPin, 2000); //initialize Servo objects with their starting values
  digitalWrite(PowerFetPin, HIGH); //start the servo power rail
  digitalWrite(EyeLEDPin, LOW); //make sure terminator eye is off
}