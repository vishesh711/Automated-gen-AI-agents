import tkinter as tk
from tkinter import scrolledtext
import webbrowser


class SuperSimpleAssistant:
    def __init__(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Super Simple Assistant")
        self.root.geometry("600x500")

        # Create the chat history display
        self.chat_history = scrolledtext.ScrolledText(self.root, state="disabled")
        self.chat_history.pack(expand=True, fill="both", padx=10, pady=10)

        # Create the input field
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill="x", padx=10, pady=10)

        self.input_field = tk.Entry(self.input_frame)
        self.input_field.pack(side=tk.LEFT, fill="x", expand=True)
        self.input_field.bind("<Return>", self.process_input)

        # Create the send button
        self.send_button = tk.Button(
            self.input_frame, text="Send", command=self.process_input
        )
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # Add initial message
        self.add_message("System", "Welcome! Try typing 'open google' or 'help'")

    def add_message(self, sender, message):
        """Add a message to the chat history"""
        self.chat_history.config(state="normal")

        if self.chat_history.index("end-1c") != "1.0":
            self.chat_history.insert(tk.END, "\n\n")

        if sender == "User":
            self.chat_history.insert(tk.END, f"You: {message}")
        elif sender == "System":
            self.chat_history.insert(tk.END, f"System: {message}")
        else:
            self.chat_history.insert(tk.END, f"Assistant: {message}")

        self.chat_history.config(state="disabled")
        self.chat_history.see(tk.END)

    def process_input(self, event=None):
        """Process user input"""
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        # Clear the input field
        self.input_field.delete(0, tk.END)

        # Add user message to chat
        self.add_message("User", user_input)

        # Process the command
        command = user_input.lower()

        if command == "help":
            self.add_message("Assistant", "Commands: 'open google', 'help', 'exit'")

        elif command == "exit":
            self.add_message("Assistant", "Goodbye!")
            self.root.after(1000, self.root.destroy)

        elif command.startswith("open"):
            parts = command.split("open", 1)
            if len(parts) > 1:
                site = parts[1].strip()
                if site == "google":
                    url = "https://www.google.com"
                elif site == "youtube":
                    url = "https://www.youtube.com"
                else:
                    if not site.startswith("http"):
                        url = "https://" + site
                    else:
                        url = site

                self.add_message("Assistant", f"Opening {url}")
                try:
                    webbrowser.open(url)
                except Exception as e:
                    self.add_message("System", f"Error opening website: {e}")
            else:
                self.add_message("Assistant", "Please specify what to open")

        else:
            self.add_message("Assistant", f"You said: {user_input}")

    def run(self):
        """Run the application"""
        # Set focus to the input field
        self.input_field.focus_set()

        # Start the main loop
        self.root.mainloop()


if __name__ == "__main__":
    app = SuperSimpleAssistant()
    app.run()
