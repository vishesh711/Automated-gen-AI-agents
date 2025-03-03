import threading
import tkinter as tk
from tkinter import scrolledtext

from utils.web_utils import (
    setup_browser,
    open_website,
    search_youtube,
    search_google,
    search_amazon,
    search_github,
    search_stackoverflow,
    take_screenshot,
    scroll_down,
    fill_form,
    click_button,
    extract_text,
)
from utils.api_utils import get_weather, get_news, save_note, get_notes
from utils.ai_utils import GPT4oAssistant

USE_GUI = True  # Set to False to run without GUI
SKIP_BROWSER = True  # Set to True to skip browser initialization


class PersonalAssistant:
    def __init__(self, use_voice=False, use_chat=True):
        self.use_voice = use_voice
        self.use_chat = use_chat
        self.browser = None
        self.setup_browser()
        self.chat_window = None
        self.chat_input = None
        self.chat_history = None
        self.ai_assistant = GPT4oAssistant()

    def setup_browser(self):
        """Initialize the web browser."""
        if SKIP_BROWSER:
            print("Skipping browser initialization for testing...")
            self.browser = None
        else:
            self.browser = setup_browser()

    def open_website(self, url):
        """Open a specific website."""
        if self.browser is None:
            print(f"Would open website: {url} (browser disabled)")
            return True
        success = open_website(self.browser, url)
        return success

    def open_linkedin(self):
        """Open LinkedIn."""
        return self.open_website("linkedin.com")

    def open_youtube(self, search_query=None):
        """Open YouTube and search for a video if query is provided."""
        if search_query:
            return search_youtube(self.browser, search_query)
        else:
            return self.open_website("youtube.com")

    def google_search(self, query):
        """Perform a Google search."""
        return search_google(self.browser, query)

    def amazon_search(self, query):
        """Search for products on Amazon."""
        return search_amazon(self.browser, query)

    def github_search(self, query):
        """Search for repositories on GitHub."""
        return search_github(self.browser, query)

    def stackoverflow_search(self, query):
        """Search for questions on Stack Overflow."""
        return search_stackoverflow(self.browser, query)

    def take_screenshot(self):
        """Take a screenshot of the current page."""
        return take_screenshot(self.browser)

    def scroll_page(self, direction="down", amount=1):
        """Scroll the page up or down."""
        return scroll_down(self.browser, direction, amount)

    def fill_form_field(self, field_name, value):
        """Fill a form field with the given value."""
        return fill_form(self.browser, field_name, value)

    def click_button_on_page(self, button_text):
        """Click a button with the given text."""
        return click_button(self.browser, button_text)

    def get_page_text(self, selector_type="body", selector_value="body"):
        """Extract text from the current page."""
        return extract_text(self.browser, selector_type, selector_value)

    def check_weather(self, city):
        """Get weather information for a city."""
        return get_weather(city)

    def get_latest_news(self):
        """Get the latest news headlines."""
        return get_news()

    def save_user_note(self, note):
        """Save a note for later reference."""
        return save_note(note)

    def get_user_notes(self):
        """Retrieve all saved notes."""
        return get_notes()

    def run(self):
        """Run the personal assistant."""
        if self.use_chat:
            self.setup_chat_interface()
            self.root.mainloop()

    def close(self):
        """Close the browser and clean up resources."""
        if self.browser:
            self.browser.quit()

    def setup_chat_interface(self):
        """Set up the chat interface using tkinter."""
        self.root = tk.Tk()
        self.root.title("AI Personal Assistant")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f5f7fa")
        self.root.minsize(800, 600)  # Set minimum window size

        # Set window icon (optional)
        try:
            self.root.iconbitmap("icon.ico")  # You can add an icon file if you have one
        except:
            pass

        # Configure the main window to be responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Add a proper window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

        # Create main frame
        main_frame = tk.Frame(self.root, bg="#f5f7fa")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header frame with logo and title
        header_frame = tk.Frame(main_frame, bg="#f5f7fa", height=60)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(1, weight=1)

        # Add a simple "logo" using a label with emoji
        logo_label = tk.Label(
            header_frame, text="🤖", font=("Arial", 24), bg="#f5f7fa", fg="#2563eb"
        )
        logo_label.grid(row=0, column=0, padx=(0, 10))

        # Title label
        title_label = tk.Label(
            header_frame,
            text="AI Personal Assistant",
            font=("Arial", 18, "bold"),
            bg="#f5f7fa",
            fg="#2563eb",
        )
        title_label.grid(row=0, column=1, sticky="w")

        # Status indicator (online/offline)
        status_indicator = tk.Frame(
            header_frame, bg="#10b981", width=12, height=12, bd=0
        )
        status_indicator.grid(row=0, column=2, padx=5)

        status_text = tk.Label(
            header_frame, text="Online", font=("Arial", 10), bg="#f5f7fa", fg="#4b5563"
        )
        status_text.grid(row=0, column=3, padx=(0, 10))

        # Chat container with rounded corners effect
        chat_container = tk.Frame(main_frame, bg="#ffffff", bd=1, relief="solid")
        chat_container.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        chat_container.grid_rowconfigure(0, weight=1)
        chat_container.grid_columnconfigure(0, weight=1)

        # Chat history display with improved styling
        self.chat_history = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            bg="white",
            font=("Arial", 11),
            state="disabled",
            borderwidth=0,
            padx=15,
            pady=15,
        )
        self.chat_history.grid(row=0, column=0, sticky="nsew")

        # Configure text tags for different message types
        self.chat_history.tag_configure(
            "user_tag", foreground="#1e40af", font=("Arial", 11, "bold")
        )
        self.chat_history.tag_configure(
            "assistant_tag", foreground="#047857", font=("Arial", 11, "bold")
        )
        self.chat_history.tag_configure(
            "user_message", foreground="#1f2937", font=("Arial", 11)
        )
        self.chat_history.tag_configure(
            "assistant_message", foreground="#374151", font=("Arial", 11)
        )
        self.chat_history.tag_configure(
            "system_message", foreground="#6b7280", font=("Arial", 10, "italic")
        )
        self.chat_history.tag_configure(
            "code_block",
            foreground="#374151",
            font=("Courier New", 10),
            background="#f3f4f6",
        )

        # Input area container
        input_container = tk.Frame(
            main_frame, bg="#ffffff", bd=1, relief="solid", height=100
        )
        input_container.grid(row=2, column=0, sticky="ew")
        input_container.grid_columnconfigure(0, weight=1)

        # Chat input with improved styling
        self.chat_input = scrolledtext.ScrolledText(
            input_container,
            height=3,
            wrap=tk.WORD,
            font=("Arial", 11),
            padx=15,
            pady=10,
            borderwidth=0,
        )
        self.chat_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.chat_input.focus_set()

        # Bind Enter key to send message (Shift+Enter for new line)
        self.chat_input.bind("<Return>", self.handle_enter)
        self.chat_input.bind(
            "<Shift-Return>", lambda e: None
        )  # Allow Shift+Enter for new line

        # Button container
        button_container = tk.Frame(input_container, bg="#ffffff")
        button_container.grid(row=0, column=1, padx=(0, 15), pady=10)

        # Send button with improved styling
        self.send_button = tk.Button(
            button_container,
            text="Send",
            command=self.send_message,
            bg="#2563eb",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
            borderwidth=0,
            cursor="hand2",
            activebackground="#1d4ed8",
            activeforeground="white",
        )
        self.send_button.pack(side=tk.TOP, pady=(0, 5))

        # Clear button
        clear_button = tk.Button(
            button_container,
            text="Clear",
            command=self.clear_chat,
            bg="#f3f4f6",
            fg="#4b5563",
            font=("Arial", 10),
            padx=15,
            pady=5,
            borderwidth=0,
            cursor="hand2",
            activebackground="#e5e7eb",
            activeforeground="#374151",
        )
        clear_button.pack(side=tk.TOP, pady=(0, 5))

        # Footer with buttons
        footer_frame = tk.Frame(main_frame, bg="#f5f7fa", height=30)
        footer_frame.grid(row=3, column=0, sticky="ew", pady=(5, 0))

        # Help button
        help_button = tk.Button(
            footer_frame,
            text="Help",
            command=self.show_help,
            bg="#f3f4f6",
            fg="#4b5563",
            font=("Arial", 10),
            padx=10,
            pady=5,
            borderwidth=0,
            cursor="hand2",
        )
        help_button.pack(side=tk.LEFT, padx=(0, 10))

        # Exit button
        exit_button = tk.Button(
            footer_frame,
            text="Exit",
            command=self.close_application,
            bg="#ef4444",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=5,
            borderwidth=0,
            cursor="hand2",
        )
        exit_button.pack(side=tk.LEFT)

        # Version info
        version_label = tk.Label(
            footer_frame, text="v1.0.0", font=("Arial", 9), bg="#f5f7fa", fg="#9ca3af"
        )
        version_label.pack(side=tk.RIGHT)

        # Display welcome message
        self.add_message(
            "system",
            "Welcome to your AI Personal Assistant! Type 'help' to see what I can do.",
        )
        self.add_message(
            "Assistant",
            "Hello! I'm your AI personal assistant. How can I help you today?",
        )

    def show_help(self):
        """Show help information."""
        help_text = """
        Here's what I can do:
        
        • Open websites: "Open example.com"
        • Search YouTube: "Search YouTube for python tutorials"
        • Search Google: "Google search for weather in New York"
        • Search Amazon: "Find headphones on Amazon"
        • Search GitHub: "Look for React libraries on GitHub"
        • Search Stack Overflow: "Find Python error handling on Stack Overflow"
        • Take screenshots: "Take a screenshot"
        • Scroll pages: "Scroll down" or "Scroll up"
        • Click buttons: "Click the Submit button"
        • Extract text: "Extract text from the page"
        • Check weather: "What's the weather in London?"
        • Get news: "Show me the latest news"
        • Save notes: "Save note: Remember to buy milk"
        • Read notes: "Show my notes"
        • General questions: Just ask anything!
        • Clear chat: "Clear chat history"
        • Exit: "Exit" or "Quit"
        """
        self.add_message("Assistant", help_text)

    def add_message(self, sender, message):
        """Add a message to the chat history."""
        self.chat_history.configure(state="normal")

        # Add a newline if there's already content
        if self.chat_history.index("end-1c") != "1.0":
            self.chat_history.insert(tk.END, "\n\n")

        # Format based on sender type
        if sender.lower() == "system":
            # System messages (notifications, etc.)
            self.chat_history.insert(tk.END, message, "system_message")
        elif sender == "User":
            # User messages
            self.chat_history.insert(tk.END, f"{sender}: ", "user_tag")

            # Check for code blocks in user messages
            if "```" in message:
                parts = message.split("```")
                self.chat_history.insert(tk.END, parts[0], "user_message")

                for i in range(1, len(parts)):
                    if i % 2 == 1:  # This is a code block
                        self.chat_history.insert(tk.END, "\n\n")
                        self.chat_history.insert(tk.END, parts[i], "code_block")
                        self.chat_history.insert(tk.END, "\n\n")
                    else:  # This is regular text
                        self.chat_history.insert(tk.END, parts[i], "user_message")
            else:
                self.chat_history.insert(tk.END, message, "user_message")
        else:
            # Assistant messages
            self.chat_history.insert(tk.END, f"{sender}: ", "assistant_tag")

            # Check for code blocks in assistant messages
            if "```" in message:
                parts = message.split("```")
                self.chat_history.insert(tk.END, parts[0], "assistant_message")

                for i in range(1, len(parts)):
                    if i % 2 == 1:  # This is a code block
                        self.chat_history.insert(tk.END, "\n\n")
                        self.chat_history.insert(tk.END, parts[i], "code_block")
                        self.chat_history.insert(tk.END, "\n\n")
                    else:  # This is regular text
                        self.chat_history.insert(tk.END, parts[i], "assistant_message")
            else:
                self.chat_history.insert(tk.END, message, "assistant_message")

        self.chat_history.configure(state="disabled")
        self.chat_history.see(tk.END)  # Scroll to the end

    def send_message(self):
        """Send a message from the chat input."""
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return

        # Clear the input field
        self.chat_input.delete("1.0", tk.END)

        # Add the message to the chat history
        self.add_message("User", message)

        # Process the command
        threading.Thread(
            target=self.handle_chat_command, args=(message,), daemon=True
        ).start()

    def handle_chat_command(self, command):
        """Process a command from the chat interface."""
        # First, try to analyze the command with GPT-4o
        try:
            command_analysis = self.ai_assistant.analyze_command(command)
            command_type = command_analysis.get("command_type", "chat")
            parameters = command_analysis.get("parameters", {})

            # Handle different command types
            if command_type == "website":
                website = parameters.get("website", "")
                if website:
                    success = self.open_website(website)
                    if success:
                        self.add_message("Assistant", f"Opening {website}...")
                    else:
                        self.add_message("Assistant", f"Failed to open {website}.")
                else:
                    self.add_message("Assistant", "Please specify a website to open.")

            elif command_type == "youtube":
                query = parameters.get("query", "")
                if query:
                    success = self.open_youtube(query)
                    if success:
                        self.add_message(
                            "Assistant", f"Searching YouTube for '{query}'..."
                        )
                    else:
                        self.add_message(
                            "Assistant", f"Failed to search YouTube for '{query}'."
                        )
                else:
                    success = self.open_youtube()
                    if success:
                        self.add_message("Assistant", "Opening YouTube...")
                    else:
                        self.add_message("Assistant", "Failed to open YouTube.")

            elif command_type == "google":
                query = parameters.get("query", "")
                if query:
                    success = self.google_search(query)
                    if success:
                        self.add_message(
                            "Assistant", f"Searching Google for '{query}'..."
                        )
                    else:
                        self.add_message(
                            "Assistant", f"Failed to search Google for '{query}'."
                        )
                else:
                    self.add_message("Assistant", "Please specify what to search for.")

            elif command_type == "amazon":
                query = parameters.get("query", "")
                if query:
                    success = self.amazon_search(query)
                    if success:
                        self.add_message(
                            "Assistant", f"Searching Amazon for '{query}'..."
                        )
                    else:
                        self.add_message(
                            "Assistant", f"Failed to search Amazon for '{query}'."
                        )
                else:
                    self.add_message(
                        "Assistant", "Please specify what to search for on Amazon."
                    )

            elif command_type == "github":
                query = parameters.get("query", "")
                if query:
                    success = self.github_search(query)
                    if success:
                        self.add_message(
                            "Assistant", f"Searching GitHub for '{query}'..."
                        )
                    else:
                        self.add_message(
                            "Assistant", f"Failed to search GitHub for '{query}'."
                        )
                else:
                    self.add_message(
                        "Assistant", "Please specify what to search for on GitHub."
                    )

            elif command_type == "stackoverflow":
                query = parameters.get("query", "")
                if query:
                    success = self.stackoverflow_search(query)
                    if success:
                        self.add_message(
                            "Assistant", f"Searching Stack Overflow for '{query}'..."
                        )
                    else:
                        self.add_message(
                            "Assistant",
                            f"Failed to search Stack Overflow for '{query}'.",
                        )
                else:
                    self.add_message(
                        "Assistant",
                        "Please specify what to search for on Stack Overflow.",
                    )

            elif command_type == "screenshot":
                screenshot_path = self.take_screenshot()
                if screenshot_path:
                    self.add_message(
                        "Assistant", f"Screenshot saved to {screenshot_path}"
                    )
                else:
                    self.add_message("Assistant", "Failed to take screenshot.")

            elif command_type == "scroll":
                direction = parameters.get("direction", "down")
                amount = parameters.get("amount", 1)
                success = self.scroll_page(direction, amount)
                if success:
                    self.add_message("Assistant", f"Scrolled {direction}.")
                else:
                    self.add_message("Assistant", f"Failed to scroll {direction}.")

            elif command_type == "click":
                button_text = parameters.get("button_text", "")
                if button_text:
                    success = self.click_button_on_page(button_text)
                    if success:
                        self.add_message("Assistant", f"Clicked on '{button_text}'.")
                    else:
                        self.add_message(
                            "Assistant", f"Failed to find and click on '{button_text}'."
                        )
                else:
                    self.add_message(
                        "Assistant", "Please specify which button to click."
                    )

            elif command_type == "extract":
                selector_type = parameters.get("selector_type", "body")
                selector_value = parameters.get("selector_value", "body")
                text = self.get_page_text(selector_type, selector_value)
                self.add_message("Assistant", f"Extracted text:\n\n{text}")

            elif command_type == "weather":
                city = parameters.get("city", "")
                if city:
                    weather_info = self.check_weather(city)
                    self.add_message("Assistant", weather_info)
                else:
                    self.add_message(
                        "Assistant", "Please specify a city to check the weather for."
                    )

            elif command_type == "news":
                news = self.get_latest_news()
                self.add_message("Assistant", news)

            elif command_type == "note_save":
                note = parameters.get("note", "")
                if note:
                    result = self.save_user_note(note)
                    self.add_message("Assistant", result)
                else:
                    self.add_message("Assistant", "Please provide a note to save.")

            elif command_type == "note_read":
                notes = self.get_user_notes()
                self.add_message("Assistant", notes)

            elif command_type == "help":
                self.show_help()

            elif command_type == "exit":
                self.add_message("Assistant", "Goodbye! Closing the assistant...")
                # Use after to give time for the message to be displayed
                self.root.after(1000, self.close_application)

            elif command_type == "chat":
                # For general conversation, use GPT-4o
                response = self.ai_assistant.ask(command)
                self.add_message("Assistant", response)

            elif command_type == "clear":
                self.clear_chat()

            else:
                # Default to chat if command type is not recognized
                response = self.ai_assistant.ask(command)
                self.add_message("Assistant", response)

        except Exception as e:
            self.add_message("Assistant", f"Error processing your request: {str(e)}")
            # Fall back to general chat
            try:
                response = self.ai_assistant.ask(command)
                self.add_message("Assistant", response)
            except:
                self.add_message(
                    "Assistant", "I'm having trouble understanding. Please try again."
                )

    def clear_chat(self):
        """Clear the chat history."""
        self.chat_history.configure(state="normal")
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.configure(state="disabled")
        self.add_message("Assistant", "Chat history cleared.")

    def close_application(self):
        """Properly close the application."""
        print("Closing application...")
        if self.browser:
            try:
                self.browser.quit()
            except Exception as e:
                print(f"Error closing browser: {e}")

        try:
            self.root.destroy()
        except Exception as e:
            print(f"Error destroying root window: {e}")

        # Force exit
        import sys

        sys.exit(0)

    def handle_enter(self, event):
        """Handle Enter key press in the chat input."""
        # If Shift+Enter is pressed, allow normal behavior (new line)
        if event.state & 0x1:  # Check if Shift is pressed
            return

        # Otherwise, send the message and prevent the default behavior
        self.send_message()
        return "break"  # Prevents the default behavior (new line)


# Run the assistant if this script is executed directly
if __name__ == "__main__":
    try:
        import config
    except ImportError:
        print(
            "Config Missing: config.py file not found. Some features will be limited."
        )
        print("Please create a config.py file with your API keys.")

    # Start the assistant
    if USE_GUI:
        assistant = PersonalAssistant(use_voice=False, use_chat=True)
        try:
            assistant.run()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            assistant.close()
    else:
        # Command-line version
        print("Starting AI Assistant in command-line mode...")
        assistant = PersonalAssistant(use_voice=False, use_chat=False)

        try:
            while True:
                command = input("\nEnter a command (or 'exit' to quit): ")
                if command.lower() == "exit":
                    print("Goodbye!")
                    break

                # Process the command
                try:
                    result = assistant.ai_assistant.analyze_command(command)
                    command_type = result.get("command_type", "chat")
                    parameters = result.get("parameters", {})

                    print(f"\nCommand type: {command_type}")

                    # Handle different command types
                    if command_type == "website":
                        url = parameters.get("url", "")
                        if url:
                            success = assistant.open_website(url)
                            print(f"Opened website: {url}")
                        else:
                            print("Please specify a website URL.")

                    elif command_type == "youtube":
                        query = parameters.get("query", "")
                        if query:
                            success = assistant.open_youtube(query)
                            print(f"Searched YouTube for: {query}")
                        else:
                            success = assistant.open_youtube()
                            print("Opened YouTube.")

                    # Add more command handlers as needed

                    elif command_type == "chat":
                        response = assistant.ai_assistant.ask(command)
                        print(f"\nAssistant: {response}")

                    else:
                        response = assistant.ai_assistant.ask(command)
                        print(f"\nAssistant: {response}")

                except Exception as e:
                    print(f"Error processing your request: {str(e)}")
                    response = assistant.ai_assistant.ask(command)
                    print(f"\nAssistant: {response}")

        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            if assistant.browser:
                assistant.browser.quit()
