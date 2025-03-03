import json
import os
from datetime import datetime

import requests

try:
    from config import NEWS_API_KEY, WEATHER_API_KEY
except ImportError:
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")


def get_weather(city):
    """Get weather information for a city."""
    if not WEATHER_API_KEY:
        return "Weather API key not configured. Please add it to config.py or set as environment variable."

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            weather_info = (
                f"Weather in {city}:\n"
                f"• Condition: {weather_desc.capitalize()}\n"
                f"• Temperature: {temp}°C (feels like {feels_like}°C)\n"
                f"• Humidity: {humidity}%\n"
                f"• Wind Speed: {wind_speed} m/s"
            )
            return weather_info
        else:
            return f"Error getting weather: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error getting weather information: {str(e)}"


def get_news():
    """Get latest news headlines."""
    if not NEWS_API_KEY:
        return "News API key not configured. Please add it to config.py or set as environment variable."

    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get("status") == "ok":
            articles = data.get("articles", [])[:5]  # Get top 5 articles

            if not articles:
                return "No news articles found."

            news_text = "Latest News Headlines:\n\n"
            for i, article in enumerate(articles, 1):
                news_text += f"{i}. {article['title']}\n"
                news_text += f"   Source: {article['source']['name']}\n\n"

            return news_text
        else:
            return f"Error getting news: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error getting news information: {str(e)}"


def save_note(note):
    """Save a note to a JSON file."""
    try:
        notes_file = "notes.json"

        # Load existing notes
        if os.path.exists(notes_file):
            with open(notes_file, "r") as f:
                notes = json.load(f)
        else:
            notes = []

        # Add new note with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes.append({"timestamp": timestamp, "content": note})

        # Save updated notes
        with open(notes_file, "w") as f:
            json.dump(notes, f, indent=2)

        return f"Note saved: {note}"
    except Exception as e:
        return f"Error saving note: {str(e)}"


def get_notes():
    """Retrieve all saved notes."""
    try:
        notes_file = "notes.json"

        if not os.path.exists(notes_file):
            return "You don't have any saved notes yet."

        with open(notes_file, "r") as f:
            notes = json.load(f)

        if not notes:
            return "You don't have any saved notes yet."

        notes_text = "Your Notes:\n\n"
        for i, note in enumerate(notes, 1):
            notes_text += f"{i}. [{note['timestamp']}] {note['content']}\n\n"

        return notes_text
    except Exception as e:
        return f"Error retrieving notes: {str(e)}"
