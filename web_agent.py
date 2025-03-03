import os
import re
import secrets
import threading
import time
import webbrowser
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from utils.ai_utils import GPT4oAssistant
from utils.api_utils import get_news, get_notes, get_weather, save_note
from utils.web_utils import (
    click_button,
    extract_text,
    fill_form,
    open_website,
    scroll_down,
    search_amazon,
    search_github,
    search_google,
    search_stackoverflow,
    search_youtube,
    setup_browser,
    take_screenshot,
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key
SKIP_BROWSER = True  # Set to False to enable web automation

# Simulated user database (replace with a real database in production)
users = {
    "demo@example.com": {
        "password": "password123",  # In production, use hashed passwords
        "name": "Demo User",
    },
    "admin@sam.ai": {"password": "admin123", "name": "Admin User"},
}


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_email" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Add natural language processing capabilities
class CommandProcessor:
    def __init__(self):
        # Command patterns for better recognition
        self.command_patterns = {
            "youtube": [
                r'(?:search|find|look\s+for|show)?\s*(?:on)?\s*youtube\s+(?:for)?\s*["\']?([^"\']+)["\']?',
                r'youtube\s+(?:search|find)?\s*["\']?([^"\']+)["\']?',
                r'find\s+videos?\s+(?:of|about|on)?\s*["\']?([^"\']+)["\']?',
            ],
            "google": [
                r'(?:search|find|look\s+for)?\s*(?:on)?\s*google\s+(?:for)?\s*["\']?([^"\']+)["\']?',
                r'google\s+(?:search|find)?\s*["\']?([^"\']+)["\']?',
                r'search\s+(?:for|about)?\s*["\']?([^"\']+)["\']?',
            ],
            "weather": [
                r"(?:what\'?s?\s+the)?\s*weather\s+(?:in|at|for)?\s*([^?]+)",
                r"(?:how\'?s?\s+the)?\s*weather\s+(?:in|at|for)?\s*([^?]+)",
            ],
            "open": [
                r"open\s+(?:the\s+)?(?:website\s+)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                r"go\s+to\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                r"visit\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            ],
        }

    def extract_command(self, text):
        """Extract command and parameters from natural language input"""
        text = text.lower().strip()

        # Check for YouTube search
        for pattern in self.command_patterns["youtube"]:
            match = re.search(pattern, text)
            if match:
                query = match.group(1).strip()
                return {"command": "youtube", "query": query}

        # Check for Google search
        for pattern in self.command_patterns["google"]:
            match = re.search(pattern, text)
            if match:
                query = match.group(1).strip()
                return {"command": "google", "query": query}

        # Check for weather
        for pattern in self.command_patterns["weather"]:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                return {"command": "weather", "location": location}

        # Check for opening websites
        for pattern in self.command_patterns["open"]:
            match = re.search(pattern, text)
            if match:
                website = match.group(1).strip()
                return {"command": "open", "website": website}

        # Default to chat if no command is recognized
        return {"command": "chat", "message": text}


# Update the WebAssistant class
class WebAssistant:
    def __init__(self):
        self.browser = None if SKIP_BROWSER else setup_browser()
        self.command_processor = CommandProcessor()
        # Initialize AI assistant
        try:
            self.ai_assistant = GPT4oAssistant()
        except Exception as e:
            print(f"Error initializing AI assistant: {e}")
            # Create a fallback method if GPT4oAssistant doesn't have process_command
            self.ai_assistant = self._create_fallback_assistant()

    def _create_fallback_assistant(self):
        """Create a fallback assistant if GPT4oAssistant fails to initialize"""

        class FallbackAssistant:
            def process_command(self, text):
                return f"I understood your request: '{text}'. However, I'm currently running in fallback mode with limited capabilities."

        return FallbackAssistant()

    def process_command(self, command_text):
        """Process user command with improved understanding"""
        # First try to extract command using pattern matching
        extracted = self.command_processor.extract_command(command_text)

        if extracted["command"] == "youtube":
            query = extracted["query"]
            if SKIP_BROWSER:
                return f"I would search YouTube for '{query}', but web automation is disabled."
            else:
                search_youtube(self.browser, query)
                return f"Searching YouTube for '{query}'."

        elif extracted["command"] == "google":
            query = extracted["query"]
            if SKIP_BROWSER:
                return f"I would search Google for '{query}', but web automation is disabled."
            else:
                search_google(self.browser, query)
                return f"Searching Google for '{query}'."

        elif extracted["command"] == "weather":
            location = extracted["location"]
            weather_data = get_weather(location)
            if weather_data:
                return f"Weather in {location}: {weather_data['description']}, Temperature: {weather_data['temperature']}°C"
            else:
                return f"Sorry, I couldn't get the weather for {location}."

        elif extracted["command"] == "open":
            website = extracted["website"]
            if not website.startswith(("http://", "https://")):
                website = "https://" + website

            if SKIP_BROWSER:
                return f"I would open {website}, but web automation is disabled."
            else:
                open_website(self.browser, website)
                return f"Opening {website}."

        # If pattern matching fails or it's a chat command, use AI to understand
        else:
            try:
                # Try to use the AI assistant
                if hasattr(self.ai_assistant, "process_command"):
                    return self.ai_assistant.process_command(command_text)
                elif hasattr(self.ai_assistant, "generate_response"):
                    return self.ai_assistant.generate_response(command_text)
                else:
                    # Fallback response if no appropriate method exists
                    return f"I understood your message: '{command_text}', but I'm not sure how to respond appropriately."
            except Exception as e:
                print(f"Error processing with AI: {e}")
                return f"I received your message, but I'm having trouble processing it right now."


# Initialize the assistant
assistant = WebAssistant()


@app.route("/login", methods=["GET"])
def login():
    if "user_email" in session:
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Debug output to help diagnose the issue
    print(f"Login attempt: {email}")
    print(f"Available users: {list(users.keys())}")

    # Check if user exists and password matches
    if email in users and users[email]["password"] == password:
        # Set session variables
        session["user_email"] = email
        session["user_name"] = users[email]["name"]
        return jsonify({"success": True})
    else:
        # More detailed error message for debugging
        if email not in users:
            print(f"User {email} not found in database")
            return jsonify({"success": False, "message": "Email not registered"})
        else:
            print(f"Password mismatch for {email}")
            return jsonify({"success": False, "message": "Incorrect password"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template("index.html", user_name=session.get("user_name", "User"))


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    response = assistant.process_command(user_message)
    return jsonify({"response": response})


def open_browser():
    """Open the browser after a short delay"""
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000/login")


@app.route("/signup", methods=["GET"])
def signup():
    if "user_email" in session:
        return redirect(url_for("index"))
    return render_template("signup.html")


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields are required"})

    # Check if email already exists
    if email in users:
        return jsonify({"success": False, "message": "Email already registered"})

    # In a real application, you would hash the password before storing it
    # For example: hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Add new user to the database
    users[email] = {
        "password": password,  # In production, store hashed_password instead
        "name": name,
    }

    # Log in the new user
    session["user_email"] = email
    session["user_name"] = name

    return jsonify({"success": True})


@app.route("/api/user_info", methods=["GET"])
def user_info():
    if "user_email" in session:
        email = session["user_email"]
        if email in users:
            return jsonify(
                {
                    "logged_in": True,
                    "name": users[email]["name"],
                    "email": email,
                    "status": "Pro account",  # You can customize this based on user type
                }
            )

    return jsonify({"logged_in": False})


@app.route("/api/get_theme", methods=["GET"])
def get_theme():
    return jsonify({"theme": "dark"})


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html", user_name=session.get("user_name", "User"))


@app.route("/api/update_profile", methods=["POST"])
@login_required
def update_profile():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"success": False, "message": "Name is required"})

    email = session["user_email"]
    if email in users:
        users[email]["name"] = name
        session["user_name"] = name
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "User not found"})


@app.route("/api/update_password", methods=["POST"])
@login_required
def update_password():
    data = request.json
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"success": False, "message": "All fields are required"})

    email = session["user_email"]
    if email in users and users[email]["password"] == current_password:
        users[email]["password"] = new_password
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Current password is incorrect"})


@app.route("/api/update_preferences", methods=["POST"])
@login_required
def update_preferences():
    data = request.json
    # In a real app, you would save these preferences to a database
    # For now, we'll just return success
    return jsonify({"success": True})


@app.route("/api/update_api_keys", methods=["POST"])
@login_required
def update_api_keys():
    data = request.json
    openai_api_key = data.get("openai_api_key")

    # In a real app, you would securely store the API key
    # For now, we'll just return success
    return jsonify({"success": True})


@app.route("/api/delete_account", methods=["POST"])
@login_required
def delete_account():
    email = session["user_email"]
    if email in users:
        # Delete the user
        del users[email]
        # Clear the session
        session.clear()
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "User not found"})


@app.route("/api/chat_history", methods=["GET"])
@login_required
def get_chat_history():
    # In a real app, you would fetch this from a database
    # For now, return sample data
    return jsonify(
        {
            "history": [
                {"title": "Weather Forecast", "date": "2 hours ago"},
                {"title": "Research on AI Models", "date": "Yesterday"},
                {"title": "Travel Planning", "date": "3 days ago"},
            ]
        }
    )


@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/api/execute_command", methods=["POST"])
@login_required
def execute_command():
    """Execute a web automation command"""
    data = request.json
    command = data.get("command")
    params = data.get("params", {})

    if command == "open_website":
        url = params.get("url")
        if not url:
            return jsonify({"success": False, "message": "No URL provided"})

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            if SKIP_BROWSER:
                # Return a special response for frontend to handle
                return jsonify(
                    {
                        "success": False,
                        "message": "Web automation is disabled",
                        "url": url,
                        "fallback_available": True,
                    }
                )
            else:
                # Actually open the website using the browser
                success = open_website(url)
                return jsonify({"success": success, "message": f"Opened {url}"})
        except Exception as e:
            return jsonify(
                {
                    "success": False,
                    "message": str(e),
                    "url": url,
                    "fallback_available": True,
                }
            )

    elif command == "google_search":
        query = params.get("query")
        if not query:
            return jsonify({"success": False, "message": "No search query provided"})

        try:
            if SKIP_BROWSER:
                # Return a special response for frontend to handle
                return jsonify(
                    {
                        "success": False,
                        "message": "Web automation is disabled",
                        "query": query,
                        "fallback_available": True,
                    }
                )
            else:
                # Actually perform the search
                success = search_google(url)
                return jsonify({"success": success, "message": f"Searched for {query}"})
        except Exception as e:
            return jsonify(
                {
                    "success": False,
                    "message": str(e),
                    "query": query,
                    "fallback_available": True,
                }
            )

    return jsonify({"success": False, "message": "Unknown command"})


if __name__ == "__main__":
    # Start browser in a separate thread
    threading.Thread(target=open_browser).start()

    # Run the Flask app
    app.run(debug=True)
