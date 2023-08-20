import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import timedelta, datetime
import openai
import re
import speech_recognition as sr
import pyttsx3
import telebot


class InfluxDB:
    def __init__(self, bucket="Weather_Data"):
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

    # def query(self, measure, start):
    #     if self.query_api is None:
    #         self.query_api = self.client.query_api()
    #
    #     start = "2023-07-29T00:00:00Z"
    #
    #     query = f"""from(bucket: "{self.bucket}")
    #      |> range(start: {start})
    #      |> filter(fn: (r) => r._measurement == "{measure}")"""
    #     tables = self.query_api.query(query, org=self.org)
    #
    #     return tables

    def query_mean(self, measure, start):
        if self.query_api is None:
            self.query_api = self.client.query_api()

        query = f"""from(bucket: "{self.bucket}")
         |> range(start: {start})
         |> filter(fn: (r) => r._measurement == "{measure}")
         |> mean()"""
        tables = self.query_api.query(query, org=self.org)

        return tables


    def get_indoor_humidity(self, start_date, end_date):
        query = f"""from(bucket: "{self.bucket}")
               |> range(start: {start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {end_date.strftime('%Y-%m-%dT%H:%M:%SZ')})
               |> filter(fn: (r) => r._measurement == "indoor_humidity" and r._field == "value" and r.location == "indoor")
               |> window(every: 1d)
               |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)"""

        result = self.query(query)

        humidity_data_by_day = {day: [] for day in range(1, 4)}

        for table in result:
            for record in table.records:
                timestamp = record["_time"]
                day = (timestamp.date() - start_date.date()).days + 1
                humidity = record["_value"]
                humidity_data_by_day[day].append(humidity)

        return humidity_data_by_day

    def get_outdoor_humidity(self, start_date, end_date):
        query = f"""from(bucket: "{self.bucket}")
               |> range(start: {start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {end_date.strftime('%Y-%m-%dT%H:%M:%SZ')})
               |> filter(fn: (r) => r._measurement == "testing" and r._field == "humidity" and r.location == "outdoor")
               |> window(every: 1d)
               |> aggregateWindow(every: 1h, fn: mean, createEmpty: false) """

        result = self.query(query)

        humidity_data_by_day = {day: [] for day in range(1, 4)}

        for table in result:
            for record in table.records:
                try:
                    timestamp = record["_time"]
                    day = (timestamp.date() - start_date.date()).days + 1
                    humidity = record["_value"]
                    humidity_data_by_day[day].append(humidity)
                except:
                    continue

        return humidity_data_by_day

    def get_outdoor_temperature(self, start_date, end_date):
        query = f"""from(bucket: "{self.bucket}")
               |> range(start: {start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {end_date.strftime('%Y-%m-%dT%H:%M:%SZ')})
               |> filter(fn: (r) => r._measurement == "testing" and r._field == "temperature" and r.location == "outdoor")
               |> window(every: 1d)
               |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)"""

        result = self.query(query)

        temperature_data_by_day = {day: [] for day in range(1, 4)}

        for table in result:
            for record in table.records:
                try:
                    timestamp = record["_time"]
                    day = (timestamp.date() - start_date.date()).days + 1
                    temperature = record["_value"]
                    temperature_data_by_day[day].append(temperature)
                except:
                    continue
        return temperature_data_by_day

    def get_indoor_temperature(self, start_date, end_date):
        query = f"""from(bucket: "{self.bucket}")
            |> range(start: {start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {end_date.strftime('%Y-%m-%dT%H:%M:%SZ')})
            |> filter(fn: (r) => r._measurement == "testing" and r._field == "temperature" and r.location == "indoor")
            |> window(every: 1d)
            |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)"""

        result = self.query(query)

        temperature_data_by_day = {day: [] for day in range(1, 4)}

        for table in result:
            for record in table.records:
                try:
                    timestamp = record["_time"]
                    day = (timestamp.date() - start_date.date()).days + 1
                    temperature = record["_value"]
                    temperature_data_by_day[day].append(temperature)
                except:
                    continue

        return temperature_data_by_day

    def get_ac_status(self, start_date, end_date):
        query = f"""from(bucket: "{self.bucket}")
            |> range(start: {start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {end_date.strftime('%Y-%m-%dT%H:%M:%SZ')})
            |> filter(fn: (r) => r._measurement == "testing" and r._field == "AC_Status" and r.location == "indoor")
            |> window(every: 1d)
            |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)"""

        result = self.query(query)

        ac_status_data_by_day = {day: [] for day in range(1, 4)}

        for table in result:
            for record in table.records:
                try:
                    timestamp = record["_time"]
                    day = (timestamp.date() - start_date.date()).days + 1
                    ac_status = list(map(round,record["_value"]))
                    ac_status_data_by_day[day].append(ac_status)
                except:
                    continue

        return ac_status_data_by_day

    def get_time_data(self):


        time_data_by_day = ['00:00:00', '01:00:00', '02:00:00', '03:00:00', '04:00:00', '05:00:00', '06:00:00', '07:00:00', '08:00:00', '09:00:00', '10:00:00', '11:00:00', '12:00:00', '13:00:00', '14:00:00', '15:00:00', '16:00:00', '17:00:00', '18:00:00', '19:00:00', '20:00:00', '21:00:00', '22:00:00', '23:00:00']


        return time_data_by_day



    def query(self, query):
        if self.query_api is None:
            self.query_api = self.client.query_api()

        return self.query_api.query(query, org=self.org)

    def get_formatted_data(self, measurement, field, location, start_date, end_date):
        query = f"""from(bucket: "{self.bucket}")
            |> range(start: {start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {end_date.strftime('%Y-%m-%dT%H:%M:%SZ')})
            |> filter(fn: (r) => r._measurement == "{measurement}" and r._field == "{field}" and r.location == "{location}")
            """

        result = self.query(query)

        formatted_data_by_day = {}

        for table in result:
            for record in table.records:
                timestamp = record["_time"]
                day = (timestamp.date() - start_date.date()).days + 1

                if day not in formatted_data_by_day:
                    formatted_data_by_day[day] = {
                        "time": [],
                        "indoor Humidity": [],
                        "Outdoor Humidity Data": [],
                        "Indoor Temperature Data": [],
                        "Outdoor Temperature Data": [],
                        "AC_Status Data": []
                    }

                formatted_data_by_day[day]["time"].append(timestamp.strftime("%H:%M:%S"))
                formatted_data_by_day[day]["indoor Humidity"].append(record["_value"])
                # formatted_data_by_day[day]["Outdoor Humidity Data"].append(record["_value"])
                # formatted_data_by_day[day]["Indoor Temperature Data"].append(record["_value"])
                # formatted_data_by_day[day]["Outdoor Temperature Data"].append(record["_value"])
                # formatted_data_by_day[day]["AC_Status Data"].append(record["_value"])


        return formatted_data_by_day


token = "4S-CyOmTPUhSgUiUSf0A8Fn31keTgErGXCoxoN1makt745rOxeASQAczKo_9K8IK7i-BZDq6L2bg7Y7Qr20qLQ=="  # Replace with your InfluxDB token  # Replace with your InfluxDB token
bucket = "Weather_Data"

# Calculate the start date (last three days from July 31, 2023)
end_date = datetime(2023, 8, 1)
start_date = end_date - timedelta(days=3)

# Create an InfluxDB instance without passing the 'token' argument
influx_db = InfluxDB()

# Fetch indoor humidity data using the class method
indoor_humidity_data = influx_db.get_indoor_humidity(start_date, end_date)

# Fetch outdoor humidity data using the class method
outdoor_humidity_data = influx_db.get_outdoor_humidity(start_date, end_date)

# Fetch outdoor temperature data using the class method
outdoor_temperature_data = influx_db.get_outdoor_temperature(start_date, end_date)

# Fetch indoor temperature data using the class method
indoor_temperature_data = influx_db.get_indoor_temperature(start_date, end_date)

# Fetch AC_Status data using the class method
ac_status_data = influx_db.get_ac_status(start_date, end_date)

# Fetch time data using the class method
time_data = influx_db.get_time_data()


# # Print the time data for each day
# for day, data in time_data.items():
#     print(f"Day {day} Time Data:")
#     print(data)
#     # for time in data:
#     #     print(time)
#     # print()
#
# # Print the indoor humidity data for each day
# for day, data in indoor_humidity_data.items():
#     print(f"Day {day} indoor Humidity :")
#     print(data)
#     print()
#
# # Print the outdoor humidity data for each day
# for day, data in outdoor_humidity_data.items():
#     print(f"Day {day} Outdoor Humidity Data:")
#     print(data)
#     print()
#
# # Print the outdoor temperature data for each day
# for day, data in outdoor_temperature_data.items():
#     print(f"Day {day} Outdoor Temperature Data:")
#     print(data)
#     print()
#
# # Print the indoor temperature data for each day
# for day, data in indoor_temperature_data.items():
#     print(f"Day {day} Indoor Temperature Data:")
#     print(data)
#     print()
#
# # Print the AC_Status data for each day
# for day, data in ac_status_data.items():
#     print(f"Day {day} AC_Status Data:")
#     print(data)
#     print()

# Fetch and format data using the class method
formatted_data = influx_db.get_formatted_data("testing", "humidity", "indoor", start_date, end_date)

# Add outdoor humidity data
formatted_data_outdoor_humidity = influx_db.get_formatted_data("testing", "humidity", "outdoor", start_date, end_date)
for day, data in formatted_data_outdoor_humidity.items():
    formatted_data[day]["Outdoor Humidity Data"] = data["indoor Humidity"]

# Add indoor temperature data
formatted_data_indoor_temp = influx_db.get_formatted_data("testing", "temperature", "indoor", start_date, end_date)
for day, data in formatted_data_indoor_temp.items():
    formatted_data[day]["Indoor Temperature Data"] = data["indoor Humidity"]

# Add outdoor temperature data
formatted_data_outdoor_temp = influx_db.get_formatted_data("testing", "temperature", "outdoor", start_date, end_date)
for day, data in formatted_data_outdoor_temp.items():
    formatted_data[day]["Outdoor Temperature Data"] = data["indoor Humidity"]

# Add AC status data
formatted_data_ac_status = influx_db.get_formatted_data("testing", "AC_Status", "indoor", start_date, end_date)
for day, data in formatted_data_ac_status.items():
    formatted_data[day]["AC_Status Data"] = data["indoor Humidity"]

# Print the formatted data for each day
for day, data in formatted_data.items():
    print(f"Day {day} Data:")
    print(data)
    print()

# ... (previous code)

# Create a dictionary to store the combined data for each day
combined_data = {}


# Combine all the data into the desired format
for day, data in formatted_data.items():
    combined_data[day] = {
        "time": data["time"],
        "indoor Humidity Data": data["indoor Humidity"],
        "Outdoor Humidity Data": formatted_data_outdoor_humidity[day]["indoor Humidity"],
        "Indoor Temperature Data": formatted_data_indoor_temp[day]["indoor Humidity"],
        "Outdoor Temperature Data": formatted_data_outdoor_temp[day]["indoor Humidity"],
        "AC_Status Data": formatted_data_ac_status[day]["indoor Humidity"]
    }

# Print the combined data dictionary
print(combined_data)

# Set your OpenAI API key here
openai.api_key = "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"

# Define the data
data = combined_data


# Function to recognize speech using the microphone
def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something:")
        audio = recognizer.listen(source)

    try:
        recognized_text = recognizer.recognize_google(audio)
        print("You said:", recognized_text)
        return recognized_text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech Recognition service; {e}")
    except Exception as e:
        print("Unknown error:", e)
        return None


# Function to analyze data using OpenAI
def analyze_data(question):
    try:
        # Check if the recognized text starts with "System"
        if question.lower().startswith("system"):
            # prompt = f"""System: Analyse the following last three days time series  data  which is json format and tell me the time period based on the question. Give answer like as recommendation
            # - the (suitable or perfect or right or recommend ) time to turn on the AC (from when (AM or PM )to when(AM or PM) ) and give recomendation  why AC should be turn on in creative way
            # - do not give strange time interval like at night timing from 10 PM to 5AM dont recomend this time period
            #
            # Data: {data}
            #
            # User: {question}
            # """

            prompt =f""" Analyse the following last three days data which is in json format and recommend a time period when the ac should be turn on in morning and afternoo
                - give time period like (from when (AM or PM )to when(AM or PM) ) for each morning and afternoon
                - give reasons also
             Data: {data}
             
             User: {question}
            """

            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150,
                temperature=0.7,
            )

            answer = response.choices[0].text.strip()

            time_match = re.search(r'\d{1,2}:\d{2} [APap][Mm]', answer)
            if time_match:
                extracted_time = time_match.group()
                answer = answer.replace("[time]", extracted_time)

            return answer
        else:
            return "Please start your question with 'System'."

    except Exception as e:
        return f"Error: {e}"


# Function to play TTS audio
# Function to convert text to speech using pyttsx3
def convert_to_speech(text):
    engine = pyttsx3.init()
    # Skip speaking the "Answer" part
    if text.lower().startswith("answer"):
        text = text.split(" ", 1)[1]
    elif text.lower().startswith("system"):
        text = text.split(" ", 1)[1]
    engine.say(text)
    engine.runAndWait()



bot_token = '6505007326:AAFsm0gFmkccJR8zO3LAaoO0zwKUW_Fv2BE'
bot = telebot.TeleBot(bot_token)

# Function to send a message
def send_telegram_message(message):
    # Replace with the actual chat ID where you want to send the message
    bot_chat_id = '5906755016'


    # Check the message before sending
    if not message.strip().lower().startswith("please start your question with 'system'"):
        # Send the message
        bot.send_message(chat_id=bot_chat_id, text=message)



# Main program
def main():
    while True:
        question = recognize_speech()
        if question:
            answer = analyze_data(question)
            print(f"Q: {question}\nA: {answer}")
            convert_to_speech(answer)
            if answer.lower().startswith("answer:"):
                answer = answer.split(" ", 1)[1]
            # Send the message using the function
                send_telegram_message(answer)


if __name__ == "__main__":
    main()
