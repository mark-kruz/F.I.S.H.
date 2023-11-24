#include <Arduino.h>
#include <SerialTransfer.h>
#include <Servo.h>
#include <Wire.h>

#define PowerFetPin 0 //slight pulldown needed on this pin, to avoid MOSFET gate floating
#define EyeLEDPin 1
#define MouthServoPin 8
#define BodyServoPin 9
#define TailServoPin 10
#define TIMEOUT_DURATION 1000
#define MOUTH_TAIL_COOLDOWN 200

void servoInit(Servo servo, int pin, int value);
void updateBody();
void initElectronics();
void receiveData();
SerialTransfer fishTransfer;
Servo mouth, body, tail;