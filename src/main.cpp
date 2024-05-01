#include "header.h"

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
  servoInit(mouthServo);
  servoInit(bodyServo);
  servoInit(tailServo); //initialize Servo objects with their starting values
  digitalWrite(PowerFetPin, HIGH); //start the servo power rail
  digitalWrite(EyeLEDPin, LOW); //make sure terminator eye is off
}

void receiveData() {
  int recSize = 0;
  recSize = fishTransfer.rxObj(fishyData, recSize);
}

void servoInit(fishServo fishServo) {
  pinMode(fishServo.pin, OUTPUT);
  fishServo.servo.attach(fishServo.pin);
  fishServo.servo.writeMicroseconds(fishServo.neutral); //set servo to minimum position
}

bool checkIfTailGood(){  //interlocks the tail to not move while the mouth is moving and for a small cooldown period after
  static unsigned long lastMouthEventTime = 0;
  if (fishyData.mouthPosition != 1000) lastMouthEventTime = millis();
  if ((millis()-lastMouthEventTime >= MOUTH_TAIL_COOLDOWN)) return true;
  else return false;
}

void servoFlip(fishServo fishServo, uint8_t state){ //for flipping binary servos aka tail and body
  if (state!=0)
    {
      if (fishServo.inverted)
      {
        fishServo.servo.writeMicroseconds(fishServo.min);
      } else fishServo.servo.writeMicroseconds(fishServo.max); //if false, flip goes neutral -> max, if true, neutral -> min
    } 
    else fishServo.servo.writeMicroseconds(fishServo.neutral);
}

void writeServoUS(long input, fishServo fishServo) { //gets servo US value from the arbitrary 0-10000 given by the Python software
  //0/10000 = min/max 
  float differenceFactor = 10000/(fishServo.max-fishServo.min);
  int realMicros = (int)(input/differenceFactor)+fishServo.min;
  if (realMicros>fishServo.max) realMicros=fishServo.max;
  if (realMicros<fishServo.min) realMicros=fishServo.min; //clamp to safe values
  fishServo.servo.writeMicroseconds(realMicros);
}

void updateBody() {
  servoFlip(bodyServo, (uint8_t)fishyData.bodyState); //flips out the body based on received data
  servoFlip(tailServo, (uint8_t)fishyData.tailState); //flips out the tail based on received data
  digitalWrite(EyeLEDPin, (uint8_t)fishyData.eyeState); //turn eye on or off
  writeServoUS(fishyData.mouthPosition, mouthServo); //write mouth position to mouth
}