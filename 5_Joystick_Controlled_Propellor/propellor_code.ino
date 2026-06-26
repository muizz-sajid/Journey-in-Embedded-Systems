//button + indicator
int buttonP = 13; 
int light = 12;
int curr = 0;
int prev = 1;
bool state = false;

//joystick controls
bool control = false;
int yPin = A0;

//dc motor
int IN1 = 8;
int IN2 = 7;
int EN = 6;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(buttonP, INPUT_PULLUP);
  pinMode(light, OUTPUT);

  pinMode(yPin, INPUT);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(EN, OUTPUT);
}

void loop() {
  //put your main code here, to run repeatedly:
  int curr = digitalRead(buttonP);
  //Serial.println(curr);
  //Serial.println(prev);
    
  if (curr == 0 && prev == 1){
    state = !state;
    digitalWrite(light, state);
    control = !control;
    //Serial.println("button pressed");
  }
  prev = curr;

  while (control == true){
    int y = analogRead(yPin);
    //Serial.println(y);

    int motorVal = y * (85.0/341);
    if (y < 540){ //values vary per joystick
      motorVal = 0;;
    }

    Serial.print("Motor val: ");
    Serial.println(motorVal);

    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH); 
    analogWrite(EN, motorVal);

    int curr = digitalRead(buttonP);
    if (curr == 0){
      control = false;
      break;
    }
  }

  delay(100);


}
