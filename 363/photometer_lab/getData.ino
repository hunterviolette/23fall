const int ledPin = 13; 

void setup() {
  Serial.begin(9600);
  //pinMode(ledPin, OUTPUT);  // Set the LED pin as an output
  //digitalWrite(ledPin, HIGH);  // Turn on the LED
}

void loop() {
  // int sensorValue = analogRead(A0); 
  int sensorValue = random(0, 100);

  Serial.print("[");
  Serial.print(millis() / 1000);
  Serial.print(", ");
  Serial.print(sensorValue);
  Serial.println("]");

  delay(1000);
}