//using R1 = 330 ohms
//using R2 = 100 ohms

int pin = A1;
int readVal;
float v = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(pin, INPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  readVal = analogRead(pin);
  v = (5./1023.)*readVal;
  Serial.println(v);
  delay(700);
}
