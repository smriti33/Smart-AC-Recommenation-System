import requests
import time
import influxdb_client
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDB:
    def __init__(self, bucket="Weather_Test_Data"):
        self.token = "4S-CyOmTPUhSgUiUSf0A8Fn31keTgErGXCoxoN1makt745rOxeASQAczKo_9K8IK7i-BZDq6L2bg7Y7Qr20qLQ=="
        self.org = "Christ"
        # self.url = "http://localhost:8086"
        self.url = "http://10.21.70.16:8086"
        self.bucket = bucket
        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = None
        self.delete_api = None
        self.query_api = None

    def delete(self, measure, start, stop):
        if self.delete_api is None:
            self.delete_api = self.client.delete_api()

        #start = "1970-01-01T00:00:00Z"
        #stop = "2100-01-01T00:00:00Z"
        return self.delete_api.delete(start, stop, "_measurement="+measure, bucket=self.bucket, org=self.org)

    def write(self, measure, atag, afield):
        if self.write_api is None:
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        point = (Point(measure).tag(atag[0], atag[1]).field(afield[0], afield[1]))
        return self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def query(self, measure, start):
        if self.query_api is None:
            self.query_api = self.client.query_api()

        query = f"""from(bucket: "{self.bucket}")
         |> range(start: {start})
         |> filter(fn: (r) => r._measurement == "{measure}")"""
        tables = self.query_api.query(query, org=self.org)

        return tables

    def query_mean(self, measure, start):
        if self.query_api is None:
            self.query_api = self.client.query_api()

        query = f"""from(bucket: "{self.bucket}")
         |> range(start: {start})
         |> filter(fn: (r) => r._measurement == "{measure}")
         |> mean()"""
        tables = self.query_api.query(query, org=self.org)

        return tables

# Your existing InfluxDB class definition

# Your existing code for fetching outdoor weather data
def fetch_weather_data(city_name):
    api_key = '9e92654b6666b69de295338624d1ac4e'
    base_url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric'

    try:
        response = requests.get(base_url)
        data = response.json()

        if response.status_code == 200:
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            return temperature, humidity
        else:
            print('Error:', data['message'])
            return None, None

    except Exception as e:
        print('Error:', str(e))
        return None, None


# Your existing code for measuring indoor data


# MQTT on_message callback function
# ... (previous code)

def on_message(client, userdata, message):
    if message.topic == "tempTopic":
        temperature = float(message.payload.decode("utf-8"))
        print("Received Temperature:", temperature)
        ts.write("testing", ["location", "indoor"], ["temperature", temperature])  # Indoor temperature
    elif message.topic == "humiTopic":
        humidity = float(message.payload.decode("utf-8"))
        print("Received Humidity:", humidity)
        ts.write("testing", ["location", "indoor"], ["humidity", humidity])  # Indoor humidity

        # Fetch outdoor weather data
        city_name = 'Kolkata'
        outdoor_temperature, outdoor_humidity = fetch_weather_data(city_name)

        if outdoor_temperature is not None and outdoor_humidity is not None:
            print(f'Outdoor Temperature in {city_name}: {outdoor_temperature}°C')
            print(f'Outdoor Humidity in {city_name}: {outdoor_humidity}%')
            ts.write("outdoor_temperature", ["location", "outdoor"], ["temperature", outdoor_temperature])
            ts.write("outdoor_humidity", ["location", "outdoor"], ["humidity", outdoor_humidity])

    elif message.topic == "AcStatusTopic":
        Ac_Status = int(message.payload.decode("utf-8"))
        print("Received AC_Status:", Ac_Status)
        ts.write("testing", ["location", "indoor"], ["Ac_Status", Ac_Status])





if __name__ == '__main__':

    measure = "testing"  # Specify your measurement name

    ts = InfluxDB(bucket="Weather_Test_Data")

    # Set up MQTT client and connect to the broker using the broker address
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect("10.21.70.16", 1883)  # Replace with your MQTT broker address
    mqtt_client.subscribe([("tempTopic", 0), ("humiTopic", 0),("AcStatusTopic" , 0)])
    mqtt_client.loop_start()

    try:
        while True:
            time.sleep(120)  # Sleep for 2 minutes
    except KeyboardInterrupt:
        mqtt_client.disconnect()
        mqtt_client.loop_stop()

