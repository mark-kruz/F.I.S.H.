#include "header.h"

struct STRUCT
{
  long mouthPosition;
  long bodyState; //everything must be longs, idk why, blame python, 0 or 1
  long eyeState; //same thing, blame python
  long tailState;
} fishyData;

void setup() {
  initElectronics();
  Serial.begin(115200);
  fishTransfer.begin(Serial); //initialize servos, power on fish servo power rail, open serial transfer to backend
}

void loop() {
  static unsigned long lastRecEventTime = 0;
  if (fishTransfer.available())
  {
    receiveData();
    updateBody();
    lastRecEventTime = millis();
  } 
  if (millis()-lastRecEventTime>TIMEOUT_DURATION)
  {
    initElectronics(); //timeout to avoid mouth hanging
  }
}

void initElectronics() {
  pinMode(PowerFetPin, OUTPUT);
  pinMode(EyeLEDPin, OUTPUT); //pin config as output
  servoInit(mouth,  MouthServoPin);
  servoInit(body, BodyServoPin);
  servoInit(tail, TailServoPin); //initialize Servo objects with their starting values
  digitalWrite(PowerFetPin, HIGH); //start the servo power rail
  digitalWrite(EyeLEDPin, LOW); //make sure terminator eye is off
}

void receiveData() {
  int recSize = 0;
  recSize = fishTransfer.rxObj(fishyData, recSize);
}

void servoInit(Servo servo, int pin) {
  pinMode(pin, OUTPUT);
  servo.attach(pin);
  servo.writeMicroseconds(1000); //set servo to minimum position
}

bool checkIfTailGood(){  //interlocks the tail to not move while the mouth is moving and for a small cooldown period after
  static unsigned long lastMouthEventTime = 0;
  if (fishyData.mouthPosition != 1000) lastMouthEventTime = millis();
  if ((millis()-lastMouthEventTime >= MOUTH_TAIL_COOLDOWN)) return true;
  else return false;
}

void servoFlip(Servo servo, uint8_t state){ //for flipping binary servos aka tail and body
  if (state!=0)
  {
    servo.writeMicroseconds(2000);
  } else servo.writeMicroseconds(1000);
}

void updateBody() {
  servoFlip(body, (uint8_t)fishyData.bodyState); //flips out the body based on received data
  servoFlip(tail, (uint8_t)fishyData.tailState); //flips out the tail based on received data
  digitalWrite(EyeLEDPin, (uint8_t)fishyData.eyeState); //turn eye on or off
  mouth.writeMicroseconds(fishyData.mouthPosition); //write mouth position to mouth
}