# Weather-Notification-App
Weather Notifications Azure Function
# Overview
This Azure Function provides daily weather notifications through SMS and email. It utilizes OpenWeatherMap API for weather data, Twilio for SMS notifications, and Gmail for email alerts.

# Functionality
# get_weather(lat, lon):

Retrieves weather information from OpenWeatherMap API based on latitude and longitude.
Parameters:
lat: Latitude of the location.
lon: Longitude of the location.
# send_SMS(weather_data):

Sends an SMS notification via Twilio if there's rain predicted in the next 12 hours.
Parameters:
weather_data: Weather information obtained from get_weather function.
# temp_report(weather_data):

Generates a temperature report plot for the next 24 hours and saves it as an image.
Parameters:
weather_data: Weather information obtained from get_weather function.
# send_email(report):

Sends a daily weather report email via Gmail with the temperature plot attached.
Parameters:
report: Path to the generated temperature plot image.
# notifications_function(myTimer):

Main function triggered by a scheduled timer (every day at 7:00 AM UTC).
Initiates weather data retrieval, SMS notification, temperature report generation, and email sending.
# Configuration
Ensure that the following environment variables are set in your Azure Function App settings:

WEATHER_API_KEY: OpenWeatherMap API key.
TWILIO_SID: Twilio account SID.
TWILIO_TOKEN: Twilio authentication token.
SENDER_EMAIL: Gmail sender email.
SENDER_PASSWORD: Gmail sender email password.
RECIPIENT_EMAIL: Email address to receive weather reports.
SENDER_PNR: Twilio sender phone number.
RECIPIENT_PNR: Twilio recipient phone number.
# Dependencies
Python packages are specified in requirements.txt.
Ensure that these dependencies are installed in your Azure Function environment.
# Running Locally
To run the function locally for testing:

Install dependencies using pip install -r requirements.txt.
Set the required environment variables.
Run the function with a local function host or through the Azure Functions extension for VS Code.
