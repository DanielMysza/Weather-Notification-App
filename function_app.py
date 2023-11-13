import logging
import azure.functions as func
import requests
import smtplib
from email.message import EmailMessage
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from twilio.rest import Client
import os


# OpenWeatherMap API credentials
weather_api_key = os.environ.get("WEATHER_API_KEY")
weather_endpoint = "https://api.openweathermap.org/data/3.0/onecall"

# Twilio credentials
account_sid = os.environ.get("TWILIO_SID")
auth_token = os.environ.get("TWILIO_TOKEN")

# Gmail credentials
sender_email = os.environ.get("SENDER_EMAIL")
sender_password = os.environ.get("SENDER_PASSWORD")
recipient_email = os.environ.get("RECIPIENT_EMAIL")

# Function to get weather information
def get_weather(lat,lon):
    weather_parameters = {
        "lat": lat,
        "lon": lon,
        "appid": weather_api_key,
        "units": "metric",
        "exclude": "current,minutely,daily"
    }
    response = requests.get(weather_endpoint, params=weather_parameters)
    response.raise_for_status()
    weather_data = response.json()
    return weather_data 

# Function to send an SMS if there gonna be raining in the next 12 hours
def send_SMS(weather_data):
    will_rain = False
    weather_hourly = weather_data["hourly"][:12]
    for hour_data in weather_hourly:
        condition_code = hour_data["weather"][0]["id"]
        if int(condition_code) < 600:
            will_rain = True

# If there gonna rain, send an SMS
    if will_rain:
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
            body="There might be raining today. Don't forget your umbrella! ☂️",
            from_=os.environ.get("SENDER_PNR"),
            to=os.environ.get("RECIPIENT_PNR")
        )
        print(message.status)

# Function to create a temperature plot and save it as image
def temp_report(weather_data):
    one_day_hourly_data = weather_data["hourly"][:24]
    timestamps = [entry["dt"] for entry in one_day_hourly_data]
    temperatures = [entry["temp"] for entry in one_day_hourly_data]
    feels_like = [entry["feels_like"] for entry in one_day_hourly_data]
    humidity = [entry["humidity"] for entry in one_day_hourly_data]

# Convert timestamps to datetime objects and retrieve hours from it
    hours = [f"{datetime.utcfromtimestamp(ts).hour}:{datetime.utcfromtimestamp(ts).minute}" for ts in timestamps]

# Create a DataFrame
    df = pd.DataFrame({"Hours": hours, "Temperature": temperatures, "Perceivable temperature": feels_like, "Humidity": humidity})

# Calculate daily average humidity and 
    daily_avg_humidity = round(df['Humidity'].mean(), 2)

# Create a plot
    plt.figure(figsize=(10, 6))

# Plot temperature, Perceivable temperature
    plt.plot(df['Hours'], df['Temperature'], 'o', label='Temperature', linestyle='', markersize=8)
    for hour, temp in zip(df['Hours'], df['Temperature']):
        plt.annotate(f'{temp:.2f}°C', (hour, temp), textcoords="offset points", xytext=(0,5), ha='center', fontsize=6, color='black')

    plt.plot(df['Hours'], df['Perceivable temperature'], 'o', label='Perceivable temperature', linestyle='', markersize=8)
    for hour, feels_like in zip(df['Hours'], df['Perceivable temperature']):
        plt.annotate(f'{feels_like:.2f}°C', (hour, feels_like), textcoords="offset points", xytext=(0,5), ha='center', fontsize=6, color='black')


    plt.xlabel(f'Hour of the Day (UTC) \n AVG Humidity for today: {daily_avg_humidity}%')
    plt.ylabel('°C')
    plt.title('Temperature and AVG Humidity forecast')
    plt.xticks(fontsize=8)  # Set fontsize to be more readable
    plt.legend()

# Save the plot as an image
# Specify a writable location
    output_directory = '/tmp'
    daily_report_path = os.path.join(output_directory, 'daily_weather.png')

# Save the plot as an image
    plt.savefig(daily_report_path, bbox_inches='tight')
    plt.close()
    return daily_report_path

# Function to send the plot via e-mail
def send_email(report):
    with open('content.txt') as text:
        content = text.read()

    msg = EmailMessage()
    msg["Subject"] = "Daily weather report!"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.set_content(content)

    with open(report, 'rb') as plot:
        img_data = plot.read()
    msg.add_attachment(img_data, maintype="image", subtype="png")


    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=sender_email, password=sender_password)
        connection.send_message(msg)


app = func.FunctionApp()

@app.schedule(schedule='0 7 * * *', arg_name="myTimer", run_on_startup=True, use_monitor=False) 
def notifications_function(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    lat = 50.064651
    lon = 19.944981
    weather_data = get_weather(lat,lon)
    send_SMS(weather_data)
    report = temp_report(weather_data)
    send_email(report)