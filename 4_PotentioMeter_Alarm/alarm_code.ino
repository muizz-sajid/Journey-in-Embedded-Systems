int ledPin = 8;
int buzzPin = 13;
int potRead = A0;

int delayT = 300;

void setup() {
  // put your setup code here, to run once:
  pinMode(ledPin, OUTPUT);
  pinMode(buzzPin, OUTPUT);
  pinMode(potRead, INPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int potVal = analogRead(potVal);
  Serial.println(potVal);

  while(potVal < 800){
    digitalWrite(ledPin, HIGH);

    digitalWrite(buzzPin, HIGH);
    delayMicroseconds(delayT);
    digitalWrite(buzzPin, LOW);
    delayMicroseconds(delayT);

    potVal = analogRead(potVal);
    Serial.println(potVal);
  }
  digitalWrite(ledPin, LOW);
}
