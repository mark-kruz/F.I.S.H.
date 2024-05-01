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
#define MOUTH_TAIL_COOLDOWN 500

SerialTransfer fishTransfer;
Servo mouth, body, tail;

struct STRUCT
{
  long mouthPosition;
  long bodyState; //everything must be longs, idk why, blame python, 0 or 1
  long eyeState; //same thing, blame python
  long tailState;
} fishyData; //received data from Python

struct fishServo{
    Servo servo;
    int pin;
    int min; //minimum safe servo position
    int neutral; //centered position
    int max; //max servo pos
    bool inverted; //affects the flip function, if false, flip goes neutral -> max, if true, neutral -> min
};
fishServo bodyServo {body, BodyServoPin, 1000, 1000, 1500, false};
fishServo mouthServo {mouth, MouthServoPin, 1000, 1000, 1600, false};
fishServo tailServo {tail, TailServoPin, 1000, 1500, 1500, true}; //adjust based on needs and ranges of used servos

void servoInit(fishServo fishServo);
void updateBody();
void initElectronics();
void receiveData();