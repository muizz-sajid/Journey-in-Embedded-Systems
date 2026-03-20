int potPin = A1;
int redPin = 10;
int delayTime = 1000;

void setup() {
  // put your setup code here, to run once:
  pinMode(redPin, OUTPUT);
  pinMode(potPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  float potVal = analogRead(potPin);
  Serial.print("potentiometer value is: ");
  Serial.println(potVal) ;

  int ledVal =  (255./1023.)*potVal;
  Serial.print("Led value is: ");
  Serial.println(ledVal); 

  analogWrite(redPin, ledVal);
  delay(delayTime);
}
