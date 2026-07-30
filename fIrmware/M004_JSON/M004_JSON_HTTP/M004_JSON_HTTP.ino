/*
------------------------------------------------
Project : Portable Spotify Player
Mission : M004.2 - JSON from HTTP
Board   : ESP32-S3 N16R8
Version : 0.4.1
------------------------------------------------
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include "../../config/secrets.h"

void setup() {

  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("Portable Spotify Player");
  Serial.println("Mission 004.2");
  Serial.println("JSON from HTTP");
  Serial.println("================================");
  Serial.println();

  // -----------------------------
  // Connect to Wi-Fi
  // -----------------------------

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.println();
  Serial.println("Wi-Fi connected!");

  // -----------------------------
  // HTTP Request
  // -----------------------------

  HTTPClient http;

  http.begin("https://api.github.com");

  int httpCode = http.GET();

  Serial.print("HTTP Status: ");
  Serial.println(httpCode);

  if (httpCode == 200) {

    String payload = http.getString();

    Serial.println();
    Serial.println("Parsing JSON...");

    // -----------------------------
    // Parse JSON
    // -----------------------------

    JsonDocument doc;

    DeserializationError error = deserializeJson(doc, payload);

    if (error) {

      Serial.print("JSON parsing failed: ");
      Serial.println(error.c_str());

    } else {

      Serial.println("JSON parsing successful!");
      Serial.println();

      // Extract values
      const char* currentUser = doc["current_user_url"];
      const char* repositories = doc["repository_url"];
      const char* issues = doc["issues_url"];

      Serial.print("Current User URL : ");
      Serial.println(currentUser);

      Serial.print("Repository URL   : ");
      Serial.println(repositories);

      Serial.print("Issues URL       : ");
      Serial.println(issues);
    }

  } else {

    Serial.println("HTTP request failed.");

  }

  http.end();
}

void loop() {

}