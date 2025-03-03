import os
import sys
import threading
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import scrolledtext


class MinimalAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minimal Assistant")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

        # Configure tags for text styling
        self.setup_ui()

        # Display welcome message
        self.chat_history.insert(tk.END, "Welcome to the Minimal Assistant!\n\n")
        self.chat_history.insert(tk.END, "Try these commands:\n")
        self.chat_history.insert(tk.END, "- 'open website example.com'\n")
        self.chat_history.insert(tk.END, "- 'search google for python tutorials'\n")
        self.chat_history.insert(tk.END, "- 'search youtube for cooking videos'\n")
        self.chat_history.insert(tk.END, "- 'save note: remember to buy milk'\n")
        self.chat_history.insert(tk.END, "- 'show my notes'\n")
        self.chat_history.insert(tk.END, "- 'help'\n")
        self.chat_history.insert(tk.END, "- 'exit'\n\n")

    def setup_ui(self):
        """Set up the user interface components"""
        # Chat history area
        self.chat_history = scrolledtext.ScrolledText(self.root)
        self.chat_history.pack(expand=True, fill="both", padx=10, pady=10)
        self.chat_history.config(state="disabled")

        # Configure text tags for styling
        self.chat_history.tag_configure(
            "user", foreground="#0066cc", font=("Arial", 10, "bold")
        )
        self.chat_history.tag_configure(
            "assistant", foreground="#006633", font=("Arial", 10, "bold")
        )
        self.chat_history.tag_configure(
            "system", foreground="#666666", font=("Arial", 9, "italic")
        )

        # Input area
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill="x", padx=10, pady=10)

        self.chat_input = tk.Text(self.input_frame, height=3)
        self.chat_input.pack(side=tk.LEFT, expand=True, fill="x")
        self.chat_input.bind("<Return>", self.handle_enter)
        self.chat_input.focus_set()  # Set focus to input field

        # Buttons
        button_frame = tk.Frame(self.input_frame)
        button_frame.pack(side=tk.RIGHT)

        self.send_button = tk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            bg="#4CAF50",
            fg="white",
        )
        self.send_button.pack(side=tk.TOP, pady=2)

        self.clear_button = tk.Button(
            button_frame, text="Clear", command=self.clear_chat, bg="#f0f0f0"
        )
        self.clear_button.pack(side=tk.TOP, pady=2)

        self.exit_button = tk.Button(
            button_frame,
            text="Exit",
            command=self.close_application,
            bg="#f44336",
            fg="white",
        )
        self.exit_button.pack(side=tk.TOP, pady=2)

    def add_message(self, sender, message):
        """Add a message to the chat history with proper formatting"""
        self.chat_history.config(state="normal")

        # Add a newline if there's already content
        if self.chat_history.index("end-1c") != "1.0":
            self.chat_history.insert(tk.END, "\n\n")

        if sender == "User":
            self.chat_history.insert(tk.END, f"{sender}: ", "user")
            self.chat_history.insert(tk.END, message)
        elif sender == "Assistant":
            self.chat_history.insert(tk.END, f"{sender}: ", "assistant")
            self.chat_history.insert(tk.END, message)
        else:
            self.chat_history.insert(tk.END, message, "system")

        self.chat_history.config(state="disabled")
        self.chat_history.see(tk.END)

    def send_message(self):
        """Send a message and process it"""
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return

        # Clear the input field
        self.chat_input.delete("1.0", tk.END)

        # Add the message to the chat history
        self.add_message("User", message)

        # Process the command in a separate thread to keep UI responsive
        threading.Thread(target=self.process_command, args=(message,)).start()

    def process_command(self, command):
        """Process the user's command"""
        command = command.lower()

        # Simple command parsing
        if command == "help":
            self.show_help()

        elif command == "exit" or command == "quit":
            self.add_message("Assistant", "Goodbye! Closing the assistant...")
            self.root.after(1000, self.close_application)

        elif command.startswith("open website"):
            parts = command.split("open website", 1)
            if len(parts) > 1:
                website = parts[1].strip()
                if not website.startswith("http"):
                    website = "https://" + website
                self.add_message("Assistant", f"Opening {website}...")
                webbrowser.open(website)
            else:
                self.add_message("Assistant", "Please specify a website to open.")

        elif command.startswith("search google for"):
            query = command.replace("search google for", "", 1).strip()
            if query:
                self.add_message("Assistant", f"Searching Google for '{query}'...")
                search_url = (
                    f"https://www.google.com/search?q={query.replace(' ', '+')}"
                )
                webbrowser.open(search_url)
            else:
                self.add_message("Assistant", "Please specify what to search for.")

        elif command.startswith("search youtube for"):
            query = command.replace("search youtube for", "", 1).strip()
            if query:
                self.add_message("Assistant", f"Searching YouTube for '{query}'...")
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                webbrowser.open(search_url)
            else:
                self.add_message(
                    "Assistant", "Please specify what to search for on YouTube."
                )

        elif command.startswith("save note:"):
            note = command.replace("save note:", "", 1).strip()
            if note:
                result = self.save_note(note)
                self.add_message("Assistant", result)
            else:
                self.add_message("Assistant", "Please provide content for your note.")

        elif (
            command == "show my notes"
            or command == "read notes"
            or command == "get notes"
        ):
            notes = self.get_notes()
            self.add_message("Assistant", notes)

        elif command == "clear" or command == "clear chat":
            self.clear_chat()

        else:
            # Echo the command for demonstration purposes
            response = f"I received your command: '{command}'\n\nIn a full implementation, I would process this intelligently."
            self.add_message("Assistant", response)

    def save_note(self, note):
        """Save a note to a JSON file"""
        try:
            import json

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

    def get_notes(self):
        """Retrieve all saved notes"""
        try:
            import json

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

    def show_help(self):
        """Show help information"""
        help_text = """
Available Commands:

• open website [url] - Open a website
• search google for [query] - Search Google
• search youtube for [query] - Search YouTube
• save note: [content] - Save a note
• show my notes - View your saved notes
• clear - Clear the chat history
• help - Show this help message
• exit - Close the assistant
"""
        self.add_message("Assistant", help_text)

    def handle_enter(self, event):
        """Handle Enter key press in the chat input"""
        # If Shift+Enter is pressed, allow normal behavior (new line)
        if event.state & 0x1:  # Check if Shift is pressed
            return

        # Otherwise, send the message and prevent the default behavior
        self.send_message()
        return "break"  # Prevents the default behavior (new line)

    def clear_chat(self):
        """Clear the chat history"""
        self.chat_history.config(state="normal")
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.config(state="disabled")
        self.add_message("System", "Chat history cleared.")

    def close_application(self):
        """Properly close the application"""
        print("Closing application...")
        try:
            self.root.destroy()
        except:
            pass

        # Force exit if needed
        sys.exit(0)

    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MinimalAssistant()
    app.run()
