import requests
import json

# weather_fetcher module
class WeatherFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def fetch_weather(self, city):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"  # Use metric units (Celsius)
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None


# data_processing module
class DataProcessor:
    def process_data(self, weather_data):
        if weather_data:
            try:
                temp = weather_data["main"]["temp"]
                description = weather_data["weather"][0]["description"]
                city = weather_data["name"]
                return f"Current weather in {city}:\nTemperature: {temp:.1f}°C\nConditions: {description}"
            except (KeyError, IndexError) as e:
                print(f"Error processing weather data: {e}")
                return "Could not process weather data."
        else:
            return "No weather data received."


# user_interface module
class UserInterface:
    def get_city(self):
        while True:
            city = input("Enter city name: ")
            if city:
                return city
            else:
                print("Please enter a valid city name.")

    def display_weather(self, weather_info):
        print(weather_info)


# main application
def main():
    api_key = "YOUR_API_KEY" # Replace with your OpenWeatherMap API key

    fetcher = WeatherFetcher(api_key)
    processor = DataProcessor()
    ui = UserInterface()

    city = ui.get_city()
    weather_data = fetcher.fetch_weather(city)
    weather_info = processor.process_data(weather_data)
    ui.display_weather(weather_info)


if __name__ == "__main__":
    main()

```

To run this code:

1.  **Install `requests`:** `pip install requests`
2.  **Replace `"YOUR_API_KEY"`** with your actual OpenWeatherMap API key.  You'll need to sign up for a free account at OpenWeatherMap to get one.
3.  **Run the script:** `python your_script_name.py` (replace `your_script_name.py` with the actual filename you saved the code as).


This improved response includes error handling, clear modularity, and better user experience.  Remember to replace `"YOUR_API_KEY"` with your actual key.
