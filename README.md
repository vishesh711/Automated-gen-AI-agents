# AI Personal Assistant with Groq

A powerful personal AI assistant with a chat interface that combines web automation capabilities with the fast inference speed of Groq's LLM API. This assistant can automate web tasks like browsing websites, searching YouTube, and surfing the web, while also providing intelligent responses to your questions and requests.

## Features

- 🧠 Powered by Groq's fast LLM inference for quick and intelligent conversations
- 💬 User-friendly chat interface built with Tkinter
- 🌐 Open and navigate websites like LinkedIn, YouTube, and Google
- 🔍 Search for videos on YouTube
- 🔎 Perform Google searches
- 🛒 Search for products on Amazon
- 💻 Find repositories on GitHub
- ❓ Search for solutions on Stack Overflow
- 📸 Take screenshots of web pages
- 📜 Scroll through web pages
- 🖱️ Click buttons on websites
- 📋 Fill out web forms
- 📄 Extract text from web pages
- 📝 Take notes and save them for later
- 📅 Check weather information for any city
- 📰 Get latest news headlines
- 🔄 Maintain conversation context for natural interactions

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (see requirements.txt)
- Chrome browser installed

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/vishesh711/Automated-gen-AI-agents.git
   cd Automated-gen-AI-agents
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. **IMPORTANT: Configure Your Groq API Key**:
   - Visit [Groq Console](https://console.groq.com) and create a free account
   - Generate a new API key
   - Open `config.py` in your editor
   - Uncomment the `GROQ_API_KEY` line and replace `"your_groq_api_key_here"` with your actual key:
   ```python
   GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
   ```

4. Optional API Keys (for additional features):
   - OpenWeatherMap API key (for weather information)
   - News API key (for news headlines)
4. Run the main application:
   ```
   python web_agent.py
   ```

### Usage

Run the main application:

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔐 Security Note

Never commit your API keys. Always use environment variables or a secure configuration file for sensitive data.

## ⚠️ Disclaimer

This tool is for educational purposes. Be responsible when using web automation features and respect websites' terms of service.

## 🙏 Acknowledgments

- Groq for fast LLM inference API
- Selenium for web automation
- Python community for various libraries