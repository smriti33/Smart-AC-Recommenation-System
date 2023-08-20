#include <Ethernet.h>
#include <Wire.h>
#include <SoftWire.h>
#include <DHT.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "HardwareSerial.h"


// DHT sensor setup
#define DHTPIN 15     // Pin where the DHT11 sensor is connected
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// AC current setup
#define ACPIN 14
#define ACON_THRESHOLD 200

// Update these with values suitable for your network.
byte mac[]    = {  0xDE, 0xED, 0xBA, 78, 0xFE, 0xED };
IPAddress ip(172, 16, 0, 100);
//IPAddress server(44, 195, 202, 69);
IPAddress server(10, 21, 70, 16);

void callback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming MQTT messages based on the topic if needed
}

EthernetClient ethClient;
PubSubClient client(ethClient);

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("arduinoClient78")) {
      Serial.println("connected");
      // Once connected, resubscribe to the topics
      client.subscribe("tempTopic");
      client.subscribe("humiTopic");
      client.subscribe("ACStatusTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
    // Open serial communications and wait for port to open:
  Serial3.setRx(PC11);
  Serial3.setTx(PC10);  
  delay(50);

  Serial.begin(115200);
  //Ethernet.init(17);
  dht.begin();
  client.setServer(server, 1883);
  client.setCallback(callback);

  Ethernet.begin(mac);
  // Allow the hardware to sort itself out
  delay(1500);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read temperature and humidity from the sensor
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" °C\t");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  // Convert readings to strings
  String tempStr = String(temperature);
  String humStr = String(humidity);

  // Publish temperature and humidity readings to MQTT topics
  client.publish("tempTopic", tempStr.c_str());
  client.publish("humiTopic", humStr.c_str());

  // Publish AC status to MQTT topics
  int combinedCurrent = analogRead(ACPIN);
  Serial.println(combinedCurrent);

  if (combinedCurrent > ACON_THRESHOLD) {
    Serial.println("AC Status: ON");
    client.publish("ACStatusTopic", "1");
  } else {
    Serial.println("AC Status: OFF");
    client.publish("ACStatusTopic", "0");
  }

  // Wait for 2 minue before taking the next reading
  //delay(120000);
  delay(6000);
}