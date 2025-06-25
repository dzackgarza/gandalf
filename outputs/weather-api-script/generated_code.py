import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class UserInputHandler:
    """Handles user input for city names with validation."""

    @staticmethod
    def get_city_input():
        """Prompt user for city input and validate it."""
        while True:
            city = input("Enter a city name: ").strip()
            if city:
                return city
            print("Error: City name cannot be empty. Please try again.")

class APIRequestHandler:
    """Handles API connections and authentication."""

    def __init__(self):
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        if not self.api_key:
            raise ValueError("API key not found in environment variables.")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather_data(self, city):
        """Fetch weather data for the specified city."""
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch weather data: {str(e)}")

class DataFormatter:
    """Formats weather data into a readable string."""

    @staticmethod
    def format_weather_data(weather_data):
        """Format the weather data into a human-readable string."""
        if not weather_data:
            return "No weather data available."

        try:
            city = weather_data['name']
            country = weather_data['sys']['country']
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            conditions = weather_data['weather'][0]['description']

            return (
                f"Weather in {city}, {country}:\n"
                f"Temperature: {temp}°C\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind_speed} m/s\n"
                f"Conditions: {conditions.capitalize()}"
            )
        except KeyError as e:
            raise ValueError(f"Unexpected weather data format: missing {str(e)}")

def main():
    """Main function to run the weather fetch script."""
    print("Welcome to the Weather Fetch Script!")

    try:
        # Get user input
        city = UserInputHandler.get_city_input()

        # Fetch weather data
        api_handler = APIRequestHandler()
        weather_data = api_handler.get_weather_data(city)

        # Format and display weather data
        formatted_data = DataFormatter.format_weather_data(weather_data)
        print("\n" + formatted_data)

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please try again with a valid city name.")

if __name__ == "__main__":
    main()