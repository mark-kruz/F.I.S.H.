#include <Arduino.h>
#include <SerialTransfer.h>
#include <Servo.h>
#include <Wire.h>
#define PowerFetPin 0 //slight pulldown needed on this pin
#define EyeLEDPin 1
#define MouthServoPin 8
#define BodyServoPin 9
#define TailServoPin 10
#define TIMEOUT_DURATION 1000
#define MOUTH_TAIL_COOLDOWN 200

int millisBetweenHalfBeat;


void servoInit(Servo servo, int pin, int value);
void tailBeat();
void updateBody();
void calculateTailDelay();
void initElectronics();
void receiveData();
SerialTransfer myTransfer;
Servo mouth, body, tail;