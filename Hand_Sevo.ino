#include <ESP32Servo.h>

Servo myservo;

void setup() {
  myservo.attach(19);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {

    int angle = Serial.parseInt();

    Serial.print("Received: ");
    Serial.println(angle);

    if (Serial.available()) {
      Serial.read();
    }

    if (angle >= 0 && angle <= 180) {
      myservo.write(angle);
    }
  }
}