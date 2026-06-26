#include <Wire.h>
#include <LiquidCrystal_I2C.h>

int bPin = 4;

int totalTimesMeasured = 50;
float total = 0;
float avg;

int trigPin = 3;
int echoPin = 2;

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {

  lcd.init();
  lcd.backlight();

  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(bPin, INPUT_PULLUP);

  lcd.setCursor(0, 0);
  lcd.print("Press Button");
  lcd.setCursor(0, 1);
  lcd.print("To Measure");
}

void loop() {

  if (digitalRead(bPin) == LOW) {

    while (digitalRead(bPin) == LOW);
    delay(20);

    total = 0;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Measuring...");

    int validMeasurements = 0;

    for (int i = 0; i < totalTimesMeasured; i++) {

      float distance = measure();

      if (distance != -1) {
        total += distance;
        validMeasurements++;
      }

      delay(5);
    }

    lcd.clear();

    if (validMeasurements > 0) {

      avg = total / validMeasurements;

      Serial.print("Distance: ");
      Serial.print(avg);
      Serial.println(" cm");

      lcd.setCursor(0, 0);
      lcd.print("Distance:");

      lcd.setCursor(0, 1);
      lcd.print(avg);
      lcd.print(" cm");

    } else {

      Serial.println("No echo detected.");

      lcd.setCursor(0, 0);
      lcd.print("Measurement");
      lcd.setCursor(0, 1);
      lcd.print("Failed");
    }
  }
}

float measure() {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);

  if (duration == 0) {
    return -1;
  }

  float distance = duration * 0.0343 / 2;

  return distance;
}