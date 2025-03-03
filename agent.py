import os
import re
import sys
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import PhotoImage, filedialog, font, scrolledtext, ttk

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

USE_GUI = True
SKIP_BROWSER = False  # Set to True to skip browser initialization
APP_VERSION = "1.0.0"


class PersonalAssistant:
    def __init__(self, use_voice=False, use_chat=True):
        self.use_voice = use_voice
        self.use_chat = use_chat
        self.browser = None
        self.setup_browser()
        self.root = None
        self.chat_window = None
        self.chat_input = None
        self.chat_history = None
        self.ai_assistant = GPT4oAssistant()
        self.chat_count = 0
        self.conversation_context = []
        self.command_history = []
        self.last_command = None
        self.current_website = None

        # Theme colors - Modern light theme with accent colors
        self.colors = {
            "bg_light": "#ffffff",
            "bg_sidebar": "#f5f7fa",
            "bg_main": "#ffffff",
            "text_primary": "#333333",
            "text_secondary": "#666666",
            "accent": "#4a86e8",
            "accent_hover": "#3a76d8",
            "user_bubble": "#f0f2f5",
            "assistant_bubble": "#e9f3ff",
            "border": "#e0e0e0",
            "input_bg": "#f5f7fa",
            "button_primary": "#4a86e8",
            "button_secondary": "#f0f2f5",
        }

        # Initialize command patterns
        self.command_patterns = {
            "open_website": [
                r"open\s+(https?://[^ ]+)",
                r"open\s+([^ ]+\.[^ ]+)",
                r"open website\s+(.*)",
                r"go to\s+(.*)",
            ],
            "youtube_search": [
                r"search youtube for\s+(.*)",
                r"youtube search for\s+(.*)",
                r"find on youtube\s+(.*)",
            ],
            "google_search": [
                r"search google for\s+(.*)",
                r"google search for\s+(.*)",
                r"google\s+(search\s+.*)",
            ],
            "weather": [
                r"weather in\s+(.*)",
                r"what's the weather in\s+(.*)",
                r"what is the weather in\s+(.*)",
            ],
            "notes_save": [r"save note:\s+(.*)", r"save note\s+(.*)"],
            "notes_read": [
                r"show my notes",
                r"show notes",
                r"get notes",
                r"read notes",
                r"my notes",
            ],
            "help": [r"help"],
            "exit": [r"exit", r"quit", r"close"],
            "clear": [r"clear chat"],
            "news": [r"news", r"show news", r"latest news", r"get news"],
            "scroll": [r"scroll\s+(up|down)\s+(\d+)"],
            "click": [r"click\s+(.*)"],
            "extract": [r"extract text from the page"],
            "screenshot": [r"take a screenshot"],
            "amazon": [r"find\s+(.*)\s+on amazon"],
            "github": [r"look for\s+(.*)\s+on github"],
            "stackoverflow": [r"find\s+(.*)\s+on stack overflow"],
            "chat": [r"^.*$"],
        }

    def setup_browser(self):
        """Initialize the web browser."""
        if SKIP_BROWSER:
            print("Skipping browser initialization for testing...")
            self.browser = None
        else:
            try:
                self.browser = setup_browser()
                print("Browser initialized successfully")
            except Exception as e:
                print(f"Error initializing browser: {e}")
                self.browser = None

    def open_website(self, url):
        """Open a specific website."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        if self.browser is None:
            print(f"Opening website using webbrowser module: {url}")
            # Fallback to webbrowser module if Selenium browser is not available
            try:
                webbrowser.open(url)
                self.add_message("System", f"Opened {url} using default browser.")
                return True
            except Exception as e:
                print(f"Error opening website with default browser: {e}")
                self.add_message("System", f"Failed to open {url}. Error: {str(e)}")
                return False

        try:
            success = open_website(self.browser, url)
            if success:
                self.add_message("System", f"Successfully opened {url}")
                return True
            else:
                # If Selenium fails, fallback to webbrowser
                try:
                    webbrowser.open(url)
                    self.add_message("System", f"Opened {url} using default browser.")
                    return True
                except Exception as e:
                    self.add_message("System", f"Failed to open {url}. Error: {str(e)}")
                    return False
        except Exception as e:
            print(f"Error opening website with Selenium: {e}")
            # Fallback to webbrowser module
            try:
                webbrowser.open(url)
                self.add_message("System", f"Opened {url} using default browser.")
                return True
            except Exception as e2:
                self.add_message("System", f"Failed to open {url}. Error: {str(e2)}")
                return False

    def open_youtube(self, search_query=None):
        """Open YouTube and search for a video if query is provided."""
        if not search_query:
            return self.open_website("youtube.com")

        try:
            if self.browser is None:
                # Fallback to webbrowser module if Selenium browser is not available
                search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return True

            return search_youtube(self.browser, search_query)
        except Exception as e:
            print(f"Error searching YouTube with Selenium: {e}")
            # Fallback to webbrowser module
            search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return True

    def google_search(self, query):
        """Perform a Google search."""
        try:
            if self.browser is None:
                # Fallback to webbrowser module if Selenium browser is not available
                search_url = (
                    f"https://www.google.com/search?q={query.replace(' ', '+')}"
                )
                webbrowser.open(search_url)
                return True

            return search_google(self.browser, query)
        except Exception as e:
            print(f"Error searching Google with Selenium: {e}")
            # Fallback to webbrowser module
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return True

    def amazon_search(self, query):
        """Search for products on Amazon."""
        try:
            if self.browser is None:
                # Fallback to webbrowser module
                search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return True

            return search_amazon(self.browser, query)
        except Exception as e:
            print(f"Error searching Amazon: {e}")
            # Fallback to webbrowser module
            search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return True

    def github_search(self, query):
        """Search for repositories on GitHub."""
        try:
            if self.browser is None:
                # Fallback to webbrowser module
                search_url = f"https://github.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return True

            return search_github(self.browser, query)
        except Exception as e:
            print(f"Error searching GitHub: {e}")
            # Fallback to webbrowser module
            search_url = f"https://github.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return True

    def stackoverflow_search(self, query):
        """Search for questions on Stack Overflow."""
        try:
            if self.browser is None:
                # Fallback to webbrowser module
                search_url = (
                    f"https://stackoverflow.com/search?q={query.replace(' ', '+')}"
                )
                webbrowser.open(search_url)
                return True

            return search_stackoverflow(self.browser, query)
        except Exception as e:
            print(f"Error searching Stack Overflow: {e}")
            # Fallback to webbrowser module
            search_url = f"https://stackoverflow.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return True

    def take_screenshot(self):
        """Take a screenshot of the current page."""
        if self.browser is None:
            return "Browser is not initialized. Cannot take screenshot."

        try:
            return take_screenshot(self.browser)
        except Exception as e:
            return f"Error taking screenshot: {e}"

    def scroll_page(self, direction="down", amount=1):
        """Scroll the page up or down."""
        if self.browser is None:
            return "Browser is not initialized. Cannot scroll page."

        try:
            return scroll_down(self.browser, direction, amount)
        except Exception as e:
            return f"Error scrolling page: {e}"

    def fill_form_field(self, field_name, value):
        """Fill a form field with the given value."""
        if self.browser is None:
            return "Browser is not initialized. Cannot fill form."

        try:
            return fill_form(self.browser, field_name, value)
        except Exception as e:
            return f"Error filling form: {e}"

    def click_button_on_page(self, button_text):
        """Click a button with the given text."""
        if self.browser is None:
            return "Browser is not initialized. Cannot click button."

        try:
            return click_button(self.browser, button_text)
        except Exception as e:
            return f"Error clicking button: {e}"

    def get_page_text(self, selector_type="body", selector_value="body"):
        """Extract text from the current page."""
        if self.browser is None:
            return "Browser is not initialized. Cannot extract text."

        try:
            return extract_text(self.browser, selector_type, selector_value)
        except Exception as e:
            return f"Error extracting text: {e}"

    def check_weather(self, city):
        """Get weather information for a city."""
        try:
            return get_weather(city)
        except Exception as e:
            return f"Error checking weather: {e}"

    def get_latest_news(self):
        """Get the latest news headlines."""
        try:
            return get_news()
        except Exception as e:
            return f"Error getting news: {e}"

    def save_user_note(self, note):
        """Save a note for later reference."""
        try:
            return save_note(note)
        except Exception as e:
            return f"Error saving note: {e}"

    def get_user_notes(self):
        """Retrieve all saved notes."""
        try:
            return get_notes()
        except Exception as e:
            return f"Error retrieving notes: {e}"

    def setup_chat_interface(self):
        """Set up the chat interface with a modern, attractive design inspired by ChatAI."""
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Sam.AI")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        self.root.configure(bg=self.colors["bg_light"])
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

        # Set custom fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        self.root.option_add("*Font", default_font)

        # Create a main container with two panels
        main_container = tk.Frame(self.root, bg=self.colors["bg_light"])
        main_container.pack(fill="both", expand=True)

        # Left sidebar (250px width)
        sidebar = tk.Frame(main_container, bg=self.colors["bg_sidebar"], width=250)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)  # Prevent the frame from shrinking

        # App logo and title
        logo_frame = tk.Frame(sidebar, bg=self.colors["bg_sidebar"], height=60)
        logo_frame.pack(fill="x", padx=0, pady=(20, 10))

        logo_label = tk.Label(
            logo_frame,
            text="🤖",
            font=("Segoe UI", 24),
            bg=self.colors["bg_sidebar"],
            fg=self.colors["accent"],
        )
        logo_label.pack(side="left", padx=(20, 5))

        title_label = tk.Label(
            logo_frame,
            text="Sam.AI",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_primary"],
        )
        title_label.pack(side="left")

        # New chat button
        new_chat_button = tk.Button(
            sidebar,
            text="+ New Chat",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["accent"],
            fg="white",
            padx=15,
            pady=8,
            borderwidth=0,
            cursor="hand2",
            activebackground=self.colors["accent_hover"],
            activeforeground="white",
            command=self.clear_chat,
        )
        new_chat_button.pack(fill="x", padx=20, pady=(10, 20))

        # Search box
        search_frame = tk.Frame(sidebar, bg=self.colors["bg_sidebar"])
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        search_icon = tk.Label(
            search_frame,
            text="🔍",
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_secondary"],
        )
        search_icon.pack(side="left", padx=(5, 0))

        search_entry = tk.Entry(
            search_frame,
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_secondary"],
            insertbackground=self.colors["text_secondary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["accent"],
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        search_entry.insert(0, "Search")

        # Categories section
        categories_frame = tk.Frame(sidebar, bg=self.colors["bg_sidebar"])
        categories_frame.pack(fill="x", padx=20, pady=10)

        folder_label = tk.Label(
            categories_frame,
            text="Folder",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_primary"],
        )
        folder_label.pack(anchor="w", pady=(0, 10))

        # Sample folders
        folder_items = [("📁 General", 8), ("⭐ Favorite", 15), ("🗑️ Archive", 36)]

        for item, count in folder_items:
            folder_item_frame = tk.Frame(categories_frame, bg=self.colors["bg_sidebar"])
            folder_item_frame.pack(fill="x", pady=5)

            folder_name = tk.Label(
                folder_item_frame,
                text=item,
                bg=self.colors["bg_sidebar"],
                fg=self.colors["text_secondary"],
                anchor="w",
            )
            folder_name.pack(side="left")

            folder_count = tk.Label(
                folder_item_frame,
                text=str(count),
                bg=self.colors["bg_sidebar"],
                fg=self.colors["text_secondary"],
                anchor="e",
            )
            folder_count.pack(side="right")

        # Recent chats section
        recent_chats_frame = tk.Frame(sidebar, bg=self.colors["bg_sidebar"])
        recent_chats_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Sample recent chats
        recent_chats = [
            "What are some common UX design principles?",
            "Give me an example of effective copywriting",
            "Write a 100-character meta description",
            "Compose a blog post about AI",
        ]

        for chat in recent_chats:
            chat_item = tk.Frame(recent_chats_frame, bg=self.colors["bg_sidebar"])
            chat_item.pack(fill="x", pady=5)

            chat_icon = tk.Label(
                chat_item,
                text="💬",
                bg=self.colors["bg_sidebar"],
                fg=self.colors["text_secondary"],
            )
            chat_icon.pack(side="left", padx=(0, 5))

            # Truncate long chat titles
            chat_title = chat if len(chat) < 25 else chat[:22] + "..."

            chat_label = tk.Label(
                chat_item,
                text=chat_title,
                bg=self.colors["bg_sidebar"],
                fg=self.colors["text_secondary"],
                anchor="w",
                justify="left",
            )
            chat_label.pack(side="left", fill="x", expand=True)

            time_label = tk.Label(
                chat_item,
                text="15m",
                bg=self.colors["bg_sidebar"],
                fg=self.colors["text_secondary"],
                anchor="e",
            )
            time_label.pack(side="right")

        # Show more button
        show_more_button = tk.Button(
            recent_chats_frame,
            text="Show more ▾",
            font=("Segoe UI", 9),
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_secondary"],
            relief="flat",
            borderwidth=0,
            cursor="hand2",
        )
        show_more_button.pack(anchor="w", pady=(10, 0))

        # Bottom section with settings and user info
        bottom_frame = tk.Frame(sidebar, bg=self.colors["bg_sidebar"])
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        # Settings button
        settings_frame = tk.Frame(bottom_frame, bg=self.colors["bg_sidebar"])
        settings_frame.pack(fill="x", pady=5)

        settings_icon = tk.Label(
            settings_frame,
            text="⚙️",
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_secondary"],
        )
        settings_icon.pack(side="left", padx=(0, 5))

        settings_label = tk.Label(
            settings_frame,
            text="Settings",
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_secondary"],
            anchor="w",
        )
        settings_label.pack(side="left", fill="x", expand=True)

        # Help button
        help_frame = tk.Frame(bottom_frame, bg=self.colors["bg_sidebar"])
        help_frame.pack(fill="x", pady=5)

        help_icon = tk.Label(
            help_frame,
            text="❓",
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_secondary"],
        )
        help_icon.pack(side="left", padx=(0, 5))

        help_label = tk.Label(
            help_frame,
            text="Help",
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_secondary"],
            anchor="w",
        )
        help_label.pack(side="left", fill="x", expand=True)

        # User profile
        user_frame = tk.Frame(bottom_frame, bg=self.colors["bg_sidebar"], pady=10)
        user_frame.pack(fill="x", pady=(10, 0))

        # User avatar (circle with initials)
        user_avatar = tk.Canvas(
            user_frame,
            width=30,
            height=30,
            bg=self.colors["accent"],
            highlightthickness=0,
        )
        user_avatar.create_oval(2, 2, 28, 28, fill=self.colors["accent"], outline="")
        user_avatar.create_text(
            15, 15, text="SA", fill="white", font=("Segoe UI", 10, "bold")
        )
        user_avatar.pack(side="left", padx=(0, 10))

        # User info
        user_info = tk.Frame(user_frame, bg=self.colors["bg_sidebar"])
        user_info.pack(side="left", fill="x", expand=True)

        user_name = tk.Label(
            user_info,
            text="Sam Assistant",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_primary"],
            anchor="w",
        )
        user_name.pack(anchor="w")

        user_plan = tk.Label(
            user_info,
            text="Pro User",
            font=("Segoe UI", 8),
            bg=self.colors["bg_sidebar"],
            fg=self.colors["text_secondary"],
            anchor="w",
        )
        user_plan.pack(anchor="w")

        # Main chat area
        chat_area = tk.Frame(main_container, bg=self.colors["bg_main"])
        chat_area.pack(side="right", fill="both", expand=True)

        # Chat header
        chat_header = tk.Frame(
            chat_area, bg=self.colors["bg_main"], height=60, bd=1, relief="solid"
        )
        chat_header.pack(fill="x", side="top")
        chat_header.pack_propagate(False)

        chat_title = tk.Label(
            chat_header,
            text="Chat",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors["bg_main"],
            fg=self.colors["text_primary"],
        )
        chat_title.pack(side="left", padx=20, pady=10)

        # Theme toggle (light/dark)
        theme_frame = tk.Frame(chat_header, bg=self.colors["bg_main"])
        theme_frame.pack(side="right", padx=20)

        light_icon = tk.Label(
            theme_frame,
            text="☀️",
            bg=self.colors["bg_main"],
            fg=self.colors["text_secondary"],
            cursor="hand2",
        )
        light_icon.pack(side="left", padx=5)

        dark_icon = tk.Label(
            theme_frame,
            text="🌙",
            bg=self.colors["bg_main"],
            fg=self.colors["text_secondary"],
            cursor="hand2",
        )
        dark_icon.pack(side="left", padx=5)

        # Chat messages area
        chat_messages_frame = tk.Frame(chat_area, bg=self.colors["bg_main"])
        chat_messages_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.chat_history = tk.Text(
            chat_messages_frame,
            wrap=tk.WORD,
            bg=self.colors["bg_main"],
            fg=self.colors["text_primary"],
            font=("Segoe UI", 11),
            padx=10,
            pady=10,
            borderwidth=0,
            highlightthickness=0,
            cursor="arrow",
        )
        self.chat_history.pack(fill="both", expand=True, side="left")

        # Add scrollbar to chat history
        chat_scrollbar = ttk.Scrollbar(
            chat_messages_frame, command=self.chat_history.yview
        )
        chat_scrollbar.pack(fill="y", side="right")
        self.chat_history.configure(yscrollcommand=chat_scrollbar.set)

        # Configure text tags for styling messages
        self.chat_history.tag_configure(
            "user_bubble",
            background=self.colors["user_bubble"],
            lmargin1=20,
            lmargin2=20,
            rmargin=100,
            relief="flat",
            borderwidth=0,
            spacing1=10,
            spacing3=10,
        )

        self.chat_history.tag_configure(
            "user_text", foreground=self.colors["text_primary"], font=("Segoe UI", 11)
        )

        self.chat_history.tag_configure(
            "assistant_bubble",
            background=self.colors["assistant_bubble"],
            lmargin1=20,
            lmargin2=20,
            rmargin=100,
            relief="flat",
            borderwidth=0,
            spacing1=10,
            spacing3=10,
        )

        self.chat_history.tag_configure(
            "assistant_text",
            foreground=self.colors["text_primary"],
            font=("Segoe UI", 11),
        )

        self.chat_history.tag_configure(
            "timestamp",
            foreground=self.colors["text_secondary"],
            font=("Segoe UI", 9),
            justify="center",
        )

        self.chat_history.tag_configure(
            "system",
            foreground=self.colors["text_secondary"],
            font=("Segoe UI", 10, "italic"),
            justify="center",
            spacing1=5,
            spacing3=5,
        )

        self.chat_history.tag_configure(
            "code",
            font=("Courier New", 10),
            background="#f5f5f5",
            lmargin1=40,
            lmargin2=40,
            rmargin=40,
            spacing1=5,
            spacing3=5,
        )

        # Make chat history read-only
        self.chat_history.configure(state="disabled")

        # Bottom input area
        input_area = tk.Frame(chat_area, bg=self.colors["bg_main"], height=100)
        input_area.pack(fill="x", side="bottom", padx=20, pady=20)

        # Chat input with rounded corners and border
        input_frame = tk.Frame(
            input_area,
            bg=self.colors["bg_main"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            bd=0,
        )
        input_frame.pack(fill="x", pady=10)

        self.chat_input = tk.Text(
            input_frame,
            height=2,
            bg=self.colors["input_bg"],
            fg=self.colors["text_primary"],
            font=("Segoe UI", 11),
            padx=15,
            pady=15,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
        )
        self.chat_input.pack(side="left", fill="both", expand=True)
        self.chat_input.bind("<Return>", self.handle_enter)
        self.chat_input.bind(
            "<Shift-Return>", lambda e: None
        )  # Allow Shift+Enter for new line

        # Add placeholder text
        self.chat_input.insert("1.0", "Enter a prompt here...")
        self.chat_input.configure(fg=self.colors["text_secondary"])

        # Remove placeholder on focus
        def on_focus_in(event):
            if self.chat_input.get("1.0", "end-1c") == "Enter a prompt here...":
                self.chat_input.delete("1.0", tk.END)
                self.chat_input.configure(fg=self.colors["text_primary"])

        # Add placeholder on focus out if empty
        def on_focus_out(event):
            if not self.chat_input.get("1.0", "end-1c").strip():
                self.chat_input.delete("1.0", tk.END)
                self.chat_input.insert("1.0", "Enter a prompt here...")
                self.chat_input.configure(fg=self.colors["text_secondary"])

        self.chat_input.bind("<FocusIn>", on_focus_in)
        self.chat_input.bind("<FocusOut>", on_focus_out)

        # Voice input button (microphone icon)
        voice_button = tk.Label(
            input_frame,
            text="🎤",
            font=("Segoe UI", 16),
            bg=self.colors["input_bg"],
            fg=self.colors["text_secondary"],
            cursor="hand2",
            padx=10,
        )
        voice_button.pack(side="right")

        # Send button
        send_button = tk.Label(
            input_frame,
            text="📤",
            font=("Segoe UI", 16),
            bg=self.colors["input_bg"],
            fg=self.colors["accent"],
            cursor="hand2",
            padx=10,
        )
        send_button.pack(side="right")
        send_button.bind("<Button-1>", lambda e: self.send_message())

        # Footer with action buttons
        footer_frame = tk.Frame(input_area, bg=self.colors["bg_main"])
        footer_frame.pack(fill="x", pady=(5, 0))

        # Left side - disclaimer
        disclaimer = tk.Label(
            footer_frame,
            text="Sam.AI may produce inaccurate information.",
            font=("Segoe UI", 8),
            bg=self.colors["bg_main"],
            fg=self.colors["text_secondary"],
        )
        disclaimer.pack(side="left")

        # Right side - action buttons
        action_buttons = tk.Frame(footer_frame, bg=self.colors["bg_main"])
        action_buttons.pack(side="right")

        download_button = tk.Button(
            action_buttons,
            text="Download chat",
            font=("Segoe UI", 9),
            bg=self.colors["button_secondary"],
            fg=self.colors["text_secondary"],
            padx=10,
            pady=5,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
        )
        download_button.pack(side="left", padx=5)

        regenerate_button = tk.Button(
            action_buttons,
            text="Regenerate",
            font=("Segoe UI", 9),
            bg=self.colors["button_secondary"],
            fg=self.colors["text_secondary"],
            padx=10,
            pady=5,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
        )
        regenerate_button.pack(side="left", padx=5)

        # Set focus to input field
        self.chat_input.focus_set()

        # Add welcome message
        self.add_message(
            "Assistant",
            "Hello! I'm Sam.AI, your personal assistant. How can I help you today?",
        )

        # Configure tags for text styling
        self.chat_history.tag_configure(
            "user_tag", foreground="#4a86e8", font=("Segoe UI", 10, "bold")
        )
        self.chat_history.tag_configure(
            "user_message",
            foreground=self.colors["text_primary"],
            font=("Segoe UI", 10),
        )
        self.chat_history.tag_configure(
            "assistant_tag", foreground="#16a085", font=("Segoe UI", 10, "bold")
        )
        self.chat_history.tag_configure(
            "assistant_message",
            foreground=self.colors["text_primary"],
            font=("Segoe UI", 10),
        )
        self.chat_history.tag_configure(
            "system_tag", foreground="#e74c3c", font=("Segoe UI", 10, "bold")
        )
        self.chat_history.tag_configure(
            "system_message",
            foreground=self.colors["text_primary"],
            font=("Segoe UI", 10),
        )
        self.chat_history.tag_configure("url_link", foreground="blue", underline=1)

    def add_message(self, sender, message):
        """Add a message to the chat history with support for clickable links."""
        if self.chat_history is None:
            print(f"{sender}: {message}")
            return

        self.chat_history.configure(state="normal")

        # Add a newline if the chat history is not empty
        if self.chat_history.index("end-1c") != "1.0":
            self.chat_history.insert("end", "\n\n")

        # Format based on sender
        if sender == "User":
            self.chat_history.insert("end", "You: ", "user_tag")
            self.chat_history.insert("end", message, "user_message")
        elif sender == "System":
            self.chat_history.insert("end", "System: ", "system_tag")
            self.chat_history.insert("end", message, "system_message")
        else:
            self.chat_history.insert("end", "Assistant: ", "assistant_tag")
            self.chat_history.insert("end", message, "assistant_message")

        # Make URLs clickable
        self.make_urls_clickable()

        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

        # Add to conversation context
        self.conversation_context.append(f"{sender}: {message}")
        self.chat_count += 1

    def make_urls_clickable(self):
        """Find URLs in the latest message and make them clickable."""
        if self.chat_history is None:
            return

        # Get the last message
        last_line_start = self.chat_history.index("end-1c linestart")
        last_line_end = self.chat_history.index("end-1c")
        last_message = self.chat_history.get(last_line_start, last_line_end)

        # Find URLs using regex
        url_pattern = r"https?://[^\s]+"
        for match in re.finditer(url_pattern, last_message):
            url = match.group(0)
            start_idx = f"{last_line_start}+{match.start()}c"
            end_idx = f"{last_line_start}+{match.end()}c"

            # Remove the original text
            self.chat_history.delete(start_idx, end_idx)

            # Insert the URL as a clickable link
            self.chat_history.insert(start_idx, url, "url_link")

        # Configure the URL tag to be clickable
        self.chat_history.tag_configure("url_link", foreground="blue", underline=1)
        self.chat_history.tag_bind("url_link", "<Button-1>", self.open_url_from_tag)

    def open_url_from_tag(self, event):
        """Open the URL when clicked."""
        # Get the index of the click
        index = self.chat_history.index(f"@{event.x},{event.y}")

        # Get all tags at this position
        tags = self.chat_history.tag_names(index)

        if "url_link" in tags:
            # Find the range of the URL
            start = self.chat_history.index(f"{index} linestart")
            end = self.chat_history.index(f"{index} lineend")
            text = self.chat_history.get(start, end)

            # Extract the URL using regex
            url_pattern = r"https?://[^\s]+"
            for match in re.finditer(url_pattern, text):
                url = match.group(0)
                # Check if the click was within this URL
                url_start = self.chat_history.index(f"{start}+{match.start()}c")
                url_end = self.chat_history.index(f"{start}+{match.end()}c")
                if self.chat_history.compare(
                    url_start, "<=", index
                ) and self.chat_history.compare(index, "<=", url_end):
                    # Open the URL
                    webbrowser.open(url)
                    break

    def send_message(self):
        """Send a message from the chat input."""
        # Get message from input field
        message = self.chat_input.get("1.0", tk.END).strip()

        # Skip if it's the placeholder or empty
        if not message or message == "Enter a prompt here...":
            return

        # Clear the input field
        self.chat_input.delete("1.0", tk.END)
        self.chat_input.focus_set()  # Keep focus on input field

        # Add the message to the chat history
        self.add_message("User", message)

        # Process the command in a separate thread to keep UI responsive
        threading.Thread(
            target=self.handle_chat_command, args=(message,), daemon=True
        ).start()

    def handle_enter(self, event):
        """Handle Enter key press in the chat input."""
        # If Shift+Enter is pressed, allow normal behavior (new line)
        if event.state & 0x1:  # Check if Shift is pressed
            return

        # Otherwise, send the message and prevent the default behavior
        self.send_message()
        return "break"  # Prevents the default behavior (new line)

    def handle_chat_command(self, command):
        """Process a chat command with advanced pattern matching and context awareness."""
        command_lower = command.lower()

        # Website commands - Check this first since it's a common use case
        if (
            command_lower.startswith("open ")
            or "open website" in command_lower
            or "go to" in command_lower
        ):
            url = ""
            if command_lower.startswith("open website"):
                url = command_lower.replace("open website", "", 1).strip()
            elif command_lower.startswith("open "):
                url = command_lower.replace("open", "", 1).strip()
            elif "go to" in command_lower:
                url = command_lower.split("go to", 1)[1].strip()

            if url:
                self.add_message("Assistant", f"Opening {url}...")

                # Create a clickable link for the user
                if not url.startswith(("http://", "https://")):
                    full_url = "https://" + url
                else:
                    full_url = url

                self.add_message("System", f"Click here to open {full_url}")

                # Actually open the website
                try:
                    success = self.open_website(url)
                except Exception as e:
                    print(f"Error opening website: {e}")
                    # Fallback to webbrowser
                    try:
                        if not url.startswith(("http://", "https://")):
                            url = "https://" + url
                        webbrowser.open(url)
                        self.add_message(
                            "System", f"Opened {url} using default browser."
                        )
                    except Exception as e2:
                        self.add_message("System", f"Error opening website: {str(e2)}")
            else:
                self.add_message("Assistant", "Please specify a website to open.")
            return

        # YouTube search
        elif "youtube" in command_lower and (
            "search" in command_lower
            or "find" in command_lower
            or "play" in command_lower
        ):
            query = ""
            if "for" in command_lower:
                query = command_lower.split("for", 1)[1].strip()
            elif "play" in command_lower:
                query = command_lower.split("play", 1)[1].strip()
                if "on youtube" in query:
                    query = query.split("on youtube")[0].strip()
            else:
                # Try to extract query from the command
                parts = command_lower.split("youtube", 1)
                if len(parts) > 1:
                    query = parts[1].strip()

            if query:
                self.add_message("Assistant", f"Searching YouTube for '{query}'...")
                try:
                    success = self.open_youtube(query)
                    if not success:
                        # Fallback to webbrowser
                        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                        webbrowser.open(search_url)
                        self.add_message(
                            "System", f"Opened YouTube search in default browser."
                        )
                except Exception as e:
                    print(f"Error searching YouTube: {e}")
                    # Fallback to webbrowser
                    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    self.add_message(
                        "System", f"Opened YouTube search in default browser."
                    )
            else:
                self.add_message(
                    "Assistant", "Please specify what to search for on YouTube."
                )
            return

        # Google search
        elif "google" in command_lower and (
            "search" in command_lower or "find" in command_lower
        ):
            query = ""
            if "for" in command_lower:
                query = command_lower.split("for", 1)[1].strip()
            else:
                # Try to extract query from the command
                parts = command_lower.split("google", 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                    if query.startswith("search"):
                        query = query.replace("search", "", 1).strip()

            if query:
                self.add_message("Assistant", f"Searching Google for '{query}'...")
                try:
                    success = self.google_search(query)
                    if not success:
                        # Fallback to webbrowser
                        search_url = (
                            f"https://www.google.com/search?q={query.replace(' ', '+')}"
                        )
                        webbrowser.open(search_url)
                        self.add_message(
                            "System", f"Opened Google search in default browser."
                        )
                except Exception as e:
                    print(f"Error searching Google: {e}")
                    # Fallback to webbrowser
                    search_url = (
                        f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    )
                    webbrowser.open(search_url)
                    self.add_message(
                        "System", f"Opened Google search in default browser."
                    )
            else:
                self.add_message(
                    "Assistant", "Please specify what to search for on Google."
                )
            return

        # Weather command
        elif "weather" in command_lower:
            city = ""
            if "in" in command_lower:
                city = command_lower.split("in", 1)[1].strip()

            if city:
                self.add_message("Assistant", f"Getting weather for {city}...")
                try:
                    weather_info = get_weather(city)
                    self.add_message("Assistant", weather_info)
                except Exception as e:
                    print(f"Error getting weather: {e}")
                    self.add_message(
                        "System", f"Error getting weather information: {str(e)}"
                    )
            else:
                self.add_message(
                    "Assistant", "Please specify a city for weather information."
                )
            return

        # Notes commands
        elif command_lower.startswith("save note:") or command_lower.startswith(
            "save note "
        ):
            note = ""
            if ":" in command:
                note = command.split(":", 1)[1].strip()
            else:
                note = command.replace("save note", "", 1).strip()

            if note:
                self.add_message("Assistant", "Saving your note...")
                try:
                    result = save_note(note)
                    self.add_message("Assistant", result)
                except Exception as e:
                    print(f"Error saving note: {e}")
                    self.add_message("System", f"Error saving note: {str(e)}")
            else:
                self.add_message("Assistant", "Please provide content for your note.")
            return

        elif (
            command_lower == "show my notes"
            or command_lower == "show notes"
            or command_lower == "get notes"
        ):
            self.add_message("Assistant", "Retrieving your notes...")
            try:
                notes = get_notes()
                self.add_message("Assistant", notes)
            except Exception as e:
                print(f"Error getting notes: {e}")
                self.add_message("System", f"Error retrieving notes: {str(e)}")
            return

        # News command
        elif (
            command_lower == "news"
            or command_lower == "show news"
            or command_lower == "get news"
        ):
            self.add_message("Assistant", "Fetching the latest news headlines...")
            try:
                news_info = get_news()
                self.add_message("Assistant", news_info)
            except Exception as e:
                print(f"Error getting news: {e}")
                self.add_message("System", f"Error fetching news: {str(e)}")
            return

        # If no direct command match, use AI for general chat
        try:
            response = self.ai_assistant.ask(command)
            self.add_message("Assistant", response)
        except Exception as e:
            print(f"Error getting AI response: {e}")
            self.add_message(
                "System", "I'm having trouble understanding. Please try again."
            )

    def get_conversation_context(self):
        """Get relevant context from previous interactions."""
        if not self.conversation_context:
            return ""

        # Return the last 3 interactions as context
        return " ".join(self.conversation_context[-6:])

    def update_conversation_context(self, user_message, assistant_response):
        """Update the conversation context with the latest interaction."""
        self.conversation_context.append(f"User: {user_message}")
        self.conversation_context.append(f"Assistant: {assistant_response}")

        # Limit context size
        if len(self.conversation_context) > 20:
            self.conversation_context = self.conversation_context[-20:]

    def save_chat_history(self):
        """Save the current chat history to a file."""
        if not self.chat_history:
            return "No chat history to save."

        try:
            # Create a directory for chat history if it doesn't exist
            if not os.path.exists("chat_history"):
                os.makedirs("chat_history")

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_history/chat_{timestamp}.txt"

            # Get chat content
            self.chat_history.configure(state="normal")
            content = self.chat_history.get(1.0, tk.END)
            self.chat_history.configure(state="disabled")

            # Write to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            return f"Chat history saved to {filename}"
        except Exception as e:
            return f"Error saving chat history: {str(e)}"

    def load_chat_history(self, filename=None):
        """Load chat history from a file."""
        if not filename:
            # Open file dialog to select a file
            filename = filedialog.askopenfilename(
                initialdir="./chat_history",
                title="Select Chat History File",
                filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            )

        if not filename:
            return "No file selected."

        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            # Clear current chat and load the content
            self.chat_history.configure(state="normal")
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.insert(tk.END, content)
            self.chat_history.configure(state="disabled")
            self.chat_history.see(tk.END)

            return f"Chat history loaded from {filename}"
        except Exception as e:
            return f"Error loading chat history: {str(e)}"

    def show_advanced_help(self):
        """Show detailed help information about all capabilities."""
        help_text = """
# Sam.AI Capabilities

## Web Browsing
• Open any website: "Open example.com"
• Visit popular sites: "Open YouTube" or "Visit Wikipedia"

## Search Capabilities
• YouTube: "Search YouTube for cooking tutorials" or "Play music on YouTube"
• Google: "Google search for weather in Paris" or "Find information about quantum computing"
• Amazon: "Find headphones on Amazon" or "Search Amazon for kitchen gadgets"
• GitHub: "Look for Python libraries on GitHub"
• Stack Overflow: "Find solutions for Python errors on Stack Overflow"

## Information Services
• Weather: "What's the weather in Tokyo?" or "Weather in London"
• News: "Show me the latest news" or "Get news"

## Personal Organization
• Notes: "Save note: Call dentist on Monday" or "Remember to buy milk"
• Retrieve information: "Show my notes" or "Get notes"

## System Commands
• Help: "Show help" or "What can you do?"
• Clear chat: "Clear conversation" or "Clear chat"
• Exit: "Exit" or "Close the assistant"

Let me know if you need help with any specific feature!
"""
        self.add_message("Assistant", help_text)

    def run(self):
        """Run the personal assistant."""
        if self.use_chat:
            self.setup_chat_interface()
            self.root.mainloop()
        else:
            print("Running in console mode (not implemented yet)")

    def close_application(self):
        """Properly close the application."""
        print("Closing application...")
        if self.browser:
            try:
                self.browser.quit()
            except Exception as e:
                print(f"Error closing browser: {e}")

        try:
            if self.root:
                self.root.destroy()
        except Exception as e:
            print(f"Error destroying root window: {e}")

        # Force exit
        sys.exit(0)

    def clear_chat(self):
        """Clear the chat history."""
        if self.chat_history:
            self.chat_history.configure(state="normal")
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.configure(state="disabled")
            self.add_message("System", "Chat history cleared.")
            # Reset conversation context
            self.conversation_context = []

    def add_clickable_link(self, url, display_text=None):
        """Add a clickable link to the chat history."""
        if self.chat_history is None:
            print(f"Link: {url}")
            return

        self.chat_history.configure(state="normal")

        # Use the URL as display text if none provided
        if display_text is None:
            display_text = url

        # Insert the link
        self.chat_history.insert("end", display_text, "url_link")

        # Configure the tag
        self.chat_history.tag_configure("url_link", foreground="blue", underline=1)
        self.chat_history.tag_bind(
            "url_link", "<Button-1>", lambda e, u=url: webbrowser.open(u)
        )

        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

    def handle_website_command(self, url):
        """Handle commands to open websites with better error handling and user feedback."""
        if not url:
            self.add_message("Assistant", "Please specify a website to open.")
            return

        # Format URL properly
        if not url.startswith(("http://", "https://")):
            full_url = "https://" + url
        else:
            full_url = url

        # Add messages with clickable link
        self.add_message("Assistant", f"Opening {url}...")

        # Create a message with a clickable link
        self.chat_history.configure(state="normal")
        if self.chat_history.index("end-1c") != "1.0":
            self.chat_history.insert("end", "\n\n")
        self.chat_history.insert("end", "System: ", "system_tag")
        self.chat_history.insert("end", "Click here to open ", "system_message")
        self.chat_history.insert("end", full_url, "url_link")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

        # Configure the URL tag to be clickable
        self.chat_history.tag_configure("url_link", foreground="blue", underline=1)
        self.chat_history.tag_bind(
            "url_link", "<Button-1>", lambda e, u=full_url: webbrowser.open(u)
        )

        # Actually try to open the website
        try:
            webbrowser.open(full_url)
        except Exception as e:
            print(f"Error opening website: {e}")
            self.add_message("System", f"Error opening website: {str(e)}")


if __name__ == "__main__":
    app = PersonalAssistant(use_chat=True)
    app.run()
