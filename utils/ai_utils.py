import os
import json
import requests
from typing import Dict, Any, Optional

try:
    from config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


class GPT4oAssistant:
    """Class to handle interactions with OpenAI's GPT-4o API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the GPT-4o assistant with API key."""
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            print(
                "Warning: OpenAI API key not found. GPT-4o functionality will be limited."
            )

        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Initialize conversation history
        self.conversation_history = []
        self.max_history_length = 10  # Maximum number of message pairs to keep

    def ask(self, query: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a query to GPT-4o and get a response.

        Args:
            query: The user's question or command
            system_prompt: Optional system prompt to guide the model's behavior

        Returns:
            The model's response as a string
        """
        if not self.api_key:
            return "I can't process this request because the OpenAI API key is not configured."

        # Prepare messages
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append(
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant integrated into a personal automation tool. "
                    "Provide concise, accurate responses. If asked to perform a task that requires "
                    "web automation (like opening websites or searching), explain that you'll pass "
                    "the command to the automation system.",
                }
            )

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add the current query
        messages.append({"role": "user", "content": query})

        try:
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
            }

            # Send the request
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                # Extract the response text
                assistant_response = response_data["choices"][0]["message"]["content"]

                # Update conversation history
                self.conversation_history.append({"role": "user", "content": query})
                self.conversation_history.append(
                    {"role": "assistant", "content": assistant_response}
                )

                # Trim history if it gets too long
                if len(self.conversation_history) > self.max_history_length * 2:
                    self.conversation_history = self.conversation_history[
                        -self.max_history_length * 2 :
                    ]

                return assistant_response
            else:
                error_message = response_data.get("error", {}).get(
                    "message", "Unknown error"
                )
                return f"Error from OpenAI API: {error_message}"

        except Exception as e:
            return f"Error communicating with OpenAI API: {str(e)}"

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        return "Conversation history cleared."

    def analyze_command(self, command: str) -> Dict[str, Any]:
        """
        Analyze a user command to determine intent and extract parameters.

        Args:
            command: The user's command

        Returns:
            A dictionary with the command type and parameters
        """
        system_prompt = """
        You are a command analyzer for an AI assistant that can perform web automation tasks.
        Analyze the user's command and categorize it into one of these types:
        - website (opening a website)
        - youtube (searching YouTube)
        - google (searching Google)
        - amazon (searching Amazon)
        - github (searching GitHub)
        - stackoverflow (searching Stack Overflow)
        - screenshot (taking a screenshot)
        - scroll (scrolling the page)
        - click (clicking a button)
        - extract (extracting text from the page)
        - weather (checking weather)
        - news (getting news)
        - note_save (saving a note)
        - note_read (reading saved notes)
        - chat (general conversation)
        - help (asking for help)
        - exit (quitting the application)
        
        Extract any relevant parameters (like search queries, website names, city names, note content).
        Respond with a JSON object containing 'command_type' and 'parameters'.
        """

        try:
            response = self.ask(command, system_prompt)
            # Try to parse the response as JSON
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # If the response isn't valid JSON, return a default
            return {"command_type": "chat", "parameters": {"message": command}}
