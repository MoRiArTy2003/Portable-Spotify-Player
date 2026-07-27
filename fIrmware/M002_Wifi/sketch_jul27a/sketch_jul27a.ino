#include <WiFi.h>
#include <secrets.h>

void setup()
{
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=============================");
  Serial.println("Portable Spotify Player");
  Serial.println("=============================");
  Serial.println();

  Serial.println("Connecting to...");
  Serial.println(ssid);

  WiFi.begin(WIFI_SSID,WIFI_PASSWORD);

  while(WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.println();
  Serial.println("Connected Successfully");
  Serial.println();

  Serial.println("SSID: ");
  Serial.println(WiFi.SSID());

  Serial.println("IP Address: ");
  Serial.println(WiFi.localIP());

  Serial.print("Signal Strength (RSSI): ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");

  Serial.println("MAC Address: ");
  Serial.println(WiFi.macAddress());

  Serial.println();
  Serial.println("Ready for Mission 003");
}

void loop()
{

}