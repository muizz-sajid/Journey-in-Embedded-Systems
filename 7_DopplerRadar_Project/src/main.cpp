#include <Arduino.h>


//-------motor---------
#define STEP_PIN 7
#define DIR_PIN 6
#define EN_PIN 5

const int STEPS_180 = 100;

// 1.8 degrees per full step
const float DEGREES_PER_STEP = 1.8;

// We will keep this same value when we eventually change the system to 360 deg.
const unsigned long STEP_INTERVAL_US = 50000;

//Testing time between motor steps
// 50 ms -> 20 steps/sec
// 20 steps/sec × 1.8 deg = 36 deg/second
// Therefore:
// 180° sweep roughly 5 seconds
// 360° sweep roughly 10 seconds



//------------ultrasonic sensor-------------
#define TRIG_PIN 10
#define ECHO_PIN 11

const float MAX_DISTANCE_CM = 400.0; //max range of radar in cm

// Distance difference required to consider a measurement significantly different from the background.
const float CHANGE_THRESHOLD_CM = 30.0;

// Number of complete scans in which a target must remain present before we report it.
// This prevents one noisy scan from being treated as a target.
const int REQUIRED_SCANS = 1;

// Maximum number of target regions we can detect during one scan.
const int MAX_TARGETS = 10;





//------------ function prototypes ------------
float getDistance();

void stepMotor();

void waitForNextStep();

void takeScan();

void takeScanRev(); // probably gonna need to add a func to reset position of sensor to a known position.

void buildBackground();




// ============================================================
// SETUP
// ============================================================

void setup() {

    pinMode(STEP_PIN, OUTPUT);
    pinMode(DIR_PIN, OUTPUT);
    pinMode(EN_PIN, OUTPUT);

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    // Enable A4988
    digitalWrite(EN_PIN, LOW);

    Serial.begin(9600); // this costed me so long to figure out the baud rate was wrong, it was 9600 not 115200. kill me
    delay(2000); // Wait for serial to initialize
    buildBackground(); // Build background map before starting scans

}


// ============================================================
// MAIN LOOP
// ============================================================

void loop() {

    takeScanRev();

    takeScan();

    delay(3000); // Wait 3 second before next scan

}



// ============================================================
// ULTRASONIC DISTANCE
// ============================================================

float getDistance() {

    // Make sure trigger starts LOW
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);

    // 10 us trigger pulse
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Wait for echo (5 meters theoretical timeout)
    unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000);

    // No echo received
    if (duration == 0) {
        return -1;
    }

    // Speed of sound ≈ 0.0343 cm/us
    float distance = duration * 0.0343 / 2.0;

    // Reject impossible values
    if (distance <= 0 || distance > MAX_DISTANCE_CM) {
        return -1;
    }

    return distance;
}



// ============================================================
// MOTOR STEP
// ============================================================

void stepMotor() {

    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(2); // is the delay long enough?

    digitalWrite(STEP_PIN, LOW);
}



void takeScan() {

    digitalWrite(DIR_PIN, HIGH);

    for (int step = 0; step < STEPS_180; step++) {

        float distance = getDistance();
        float angle = step * DEGREES_PER_STEP;

        Serial.print(angle, 1);
        Serial.print(",");

        if (distance < 0) {
            Serial.print(-1);
        }
        else {
            Serial.print(distance, 1);
        }
        Serial.println(); // New line after each measurement

        delay(50); // Wait a bit before next measurement
        
        stepMotor();
    }
}


void takeScanRev() {

    digitalWrite(DIR_PIN, LOW);

    for (int step = 0; step < STEPS_180; step++) {

        float distance = getDistance();
        float angle = (STEPS_180 - step - 1) * DEGREES_PER_STEP;

        Serial.print(angle, 1);
        Serial.print(",");

        if (distance < 0) {
            Serial.print(-1);
        }
        else {
            Serial.print(distance, 1);
        }
        Serial.println(); // New line after each measurement

        delay(50); // Wait a bit before next measurement
        
        stepMotor();
    }
}


void buildBackground() {

    Serial.println();
    Serial.println("Building background map...");
    Serial.println();

    digitalWrite(DIR_PIN, HIGH);

    for (int step = 0; step < STEPS_180; step++) {

        float distance = getDistance();

        Serial.print("BG,");
        Serial.print(step);
        Serial.print(",");
        Serial.println(distance, 2);

        delay(50);

        stepMotor();
    }

    Serial.println("BG_END");

    Serial.println();
    Serial.println("Background map complete.");
    Serial.println("Beginning target detection...");
}