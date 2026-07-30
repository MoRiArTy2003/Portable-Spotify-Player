/*
---------------------------------------------------
Project: Portable Spotify Player
Mission: M004 - JSON Parsing
Board: ESP32-S3 N16RB
Version: 0.4.0
---------------------------------------------------
*/

#include <ArduinoJson.h>

void setup() {

  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("Portable Spotify Player");
  Serial.println("Mission 004 - JSON Parsing");
  Serial.println("================================");
  Serial.println();

  // Our Test JSON
  const char* json = R"rawliteral(
    {
      "name": "Ameya's Spotify Player",
      "version": "0.4.0",
      "status": "building"
    }
  )rawliteral";

  //Create JSON document
  JsonDocument doc;

  //Parse JSON
  DeserializationError error = deserializeJson(doc, json);

  //Check if parsing worked
  if (error) {
    Serial.print("JSON parsing failed: ");
    Serial.println(error.c_str());
    return;
  }

  Serial.println("JSON parsing successfull");
  Serial.println();

  //Extract values
  const char* name = doc["name"];
  const char* version = doc["version"];
  const char* status = doc["status"];

  Serial.print("Name    : ");
  Serial.println(name);

  Serial.print("Version : ");
  Serial.println(version);

  Serial.print("Status  : ");
  Serial.println(status);
}

void loop() {
}