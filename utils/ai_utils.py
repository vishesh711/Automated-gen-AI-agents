import json
import os
from typing import Any, Dict, Optional

import requests
from groq import Groq

try:
    from config import GROQ_API_KEY
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


class GroqAssistant:
    """Class to handle interactions with Groq's fast LLM API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Groq assistant with API key."""
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            print(
                "Warning: Groq API key not found. AI functionality will be limited."
            )

        # Initialize the Groq client
        try:
            self.client = Groq(api_key=self.api_key) if self.api_key else None
        except Exception as e:
            print(f"Error initializing Groq client: {e}")
            self.client = None

        # Model configuration - using a fast and capable model
        self.model = "deepseek-r1-distill-llama-70b"  # Fast reasoning model with distilled capabilities
        
        # Initialize conversation history
        self.conversation_history = []
        self.max_history_length = 10  # Maximum number of message pairs to keep

    def ask(self, query: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a query to Groq and get a response.

        Args:
            query: The user's question or command
            system_prompt: Optional system prompt to guide the model's behavior

        Returns:
            The model's response as a string
        """
        if not self.client:
            return "I can't process this request because the Groq API key is not configured."

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
            # Send the request to Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            # Extract the response text
            assistant_response = response.choices[0].message.content

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

        except Exception as e:
            return f"Error communicating with Groq API: {str(e)}"

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


# Keep backward compatibility by creating an alias
GPT4oAssistant = GroqAssistant
