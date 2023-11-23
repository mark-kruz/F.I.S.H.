#include "header.h"

struct STRUCT
{
  long mouthPosition;
  long bodyState; //boolean doesnt work, idfk why, blame python, 0 or 1
  //long eyeState; //same thing, python haram
  long tailState; //to not overspeed the mechanism by default, default to "Take me to the river" BPM
} fishyData;


void setup() {
  initElectronics();
  Serial.begin(115200);
  myTransfer.begin(Serial);
}

void loop() {
  static unsigned long lastRecEventTime = 0;
  if (myTransfer.available())
  {
    receiveData();
    updateBody();
    lastRecEventTime = millis();
  } 
  if (millis()-lastRecEventTime>TIMEOUT_DURATION)
  {
    initElectronics(); //avoid mouth hanging
  }
}

void initElectronics() {
  pinMode(PowerFetPin, OUTPUT);
  pinMode(EyeLEDPin, OUTPUT);
  servoInit(mouth,  MouthServoPin, 1000);
  servoInit(body, BodyServoPin, 1000);
  servoInit(tail, TailServoPin, 2000);
  digitalWrite(PowerFetPin, HIGH); //start the servos
  digitalWrite(EyeLEDPin, LOW); //only when commanded should the terminator eye be on
}

void receiveData() {
  int recSize = 0;
  recSize = myTransfer.rxObj(fishyData, recSize);
}

bool checkIfTailGood(){
  static unsigned long lastMouthEventTime = 0;
  if (fishyData.mouthPosition != 1000) lastMouthEventTime = millis();
  if ((millis()-lastMouthEventTime >= MOUTH_TAIL_COOLDOWN) && fishyData.tailState!=0) return true;
  else return false;
}

void updateBody() {
  if (fishyData.bodyState!=0)
  {
    body.writeMicroseconds(2000);
  } else body.writeMicroseconds(1000); //flips out the body based on received data
  if (checkIfTailGood())
  {
    tail.writeMicroseconds(1000);
  } else tail.writeMicroseconds(2000); //flips out the tail based on received data
 // digitalWrite(EyeLEDPin, fishyData.eyeState); //turn eye on or off
  mouth.writeMicroseconds(fishyData.mouthPosition); //write mouth position to mouth
}

void servoInit(Servo servo, int pin, int value) {
  pinMode(pin, OUTPUT);
  servo.attach(pin);
  servo.writeMicroseconds(value); //set servo to minimum position
}