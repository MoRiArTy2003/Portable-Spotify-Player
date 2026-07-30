#include <WiFi.h>
#include <HTTPClient.h>
#include "../../config/secrets.h"

void setup() {
  Serial.begin(115200);
  delay(1000);

  connectWiFi();

  fetchGitHubAPI();
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.println("\nConnected");
}

void fetchGitHubAPI() {
  HTTPClient http;

  http.begin("https://api.github.com");

  int httpCode = http.GET();

  Serial.print("HTTP Status Code: ");
  Serial.println(httpCode);

  if (httpCode > 0) {
    String payload = http.getString();
    Serial.println(payload);
  } else {
    Serial.println("Request Failed");
  }
  http.end();
}


void loop() {
}