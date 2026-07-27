void setup() {
  Serial.begin(115200);

  delay(3000);

  Serial.println();
  Serial.println("==============================");
  Serial.println("Portable Spotify Player");
  Serial.println("Version 0.1.0");
  Serial.println("==============================");
  Serial.println();

  Serial.println("Hello ESP32-S3!");
}

void loop() {
  Serial.println("Running...");
  delay(1000);
}