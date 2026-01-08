# 🤖 ScooVice-Discord-AI

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.4.0-blue)](https://discordpy.readthedocs.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.0.0-orange)](CHANGELOG.md)

> **The Ultimate Discord Companion** – ScooVice-Discord-AI combines advanced moderation and AI conversations in one powerful bot. Experience seamless integration with Groq AI for modern Discord communities.

## 🌟 What's New in v3.0.0 – The Final Evolution!

This is the **final major update** that transforms ScooVice-Discord-AI into the most comprehensive Discord bot available. Featuring cutting-edge AI integration and multi-language support—all designed for modern Discord communities.

- 🤖 **AI-Powered Conversations**: Natural language chat using Groq's advanced AI models.
- 🌍 **Global Language Support**: 9 languages including English, Spanish, French, German, Portuguese, Russian, Japanese, Korean, and Chinese.
- ⚡ **Enhanced Performance**: Optimized for high-traffic servers with zero downtime.

## ✨ Features

### 🛡️ **Advanced Moderation System**

- **Admin Commands**: Kick, ban, tempban, mute, unmute with permission and role checks.
- **Smart Warning System**: Automatic timeout at 3 warnings, with reset and logging.
- **Auto-Moderation**: Real-time detection of banned words, excessive caps, links, and spam.

### 🤖 **AI Chatbot**

- **Conversational AI**: Powered by Groq's Mixtral model for natural interactions.
- **Context Awareness**: Remembers conversation history for coherent chats.
- **Helpful Assistant**: Can assist with Discord-related questions and general chat.

### 🌍 **Enhanced Multi-Language Support**

- **9 Languages**: Full command translations and localized responses.
- **Per-Server Settings**: Configure language preferences per server.
- **User Preferences**: Individual language settings for personalized experience.

### 🎛️ **Customizable & Extensible**

- **Global Error Handling**: Professional responses for all errors.

### 🚀 **Performance & Reliability**

- **Async Architecture**: Handles high-traffic servers without lag.
- **Stable Sync**: Global command synchronization prevents duplicates.
- **Zero Crashes**: Comprehensive error catching and graceful failures.

## 📦 Installation

### Prerequisites

- Python 3.13+
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Groq API Key (from [Groq Console](https://console.groq.com/))

### Setup Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/ScooVice/ScooVice-Discord-AI.git
   cd ScooVice-Discord-AI
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory:

   ```
   DISCORD_TOKEN=your_bot_token_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the Bot**:

   ```bash
   python run.py
   ```

5. **Invite to Server**:
   Use the OAuth2 URL from Discord Developer Portal with `bot` and `applications.commands` scopes.

## 🎮 Usage

Once running, ScooVice-Discord-AI will automatically sync commands and display "Listening to /help | ScooVice's AI ChatBot" in its status.

### Command Categories

#### 🛡️ **Moderation Commands**

- `/kick <user> [reason]`: Remove a user from the server.
- `/ban <user> [reason]`: Permanently ban a user.
- `/tempban <user> <days> [reason]`: Temporarily ban for specified days.
- `/unban <user_id>`: Unban a user by ID.
- `/mute <user> <minutes> [reason]`: Timeout a user for minutes.
- `/unmute <user>`: Remove timeout from a user.

#### 🤖 **AI Commands**

- `/chat <message>`: Chat with the AI assistant.
- `/clear_chat`: Clear your conversation history.

#### 🎛️ **Utility Commands**

- `/help`: Display all available commands with descriptions.
- `/ping`: Check bot latency.

#### 🔧 **Auto-Moderation**

- Automatically detects and handles violations in real-time.
- Configurable banned words in `bot/cogs/automod.py`.

## 📋 Requirements

- `discord.py==2.4.0`
- `python-dotenv==1.0.1`
- `groq==0.9.0`

See `requirements.txt` for full list.

## 📜 License

This project is licensed under the GNU General Public License V3 - see the [LICENSE](LICENSE) file for details.

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and updates.

## 🏁 Project Archive Notice

**This is the final version (v3.0.0) of ScooVice-Discord-AI.** After this release, the project will be archived and no further updates will be provided. All v2 and v3 related content will be removed from scripts and GitHub.

The bot remains fully functional and ready for production use. Thank you to everyone who has used and contributed to this project over the years!

If you have suggestions or want to report bugs, visit [ScooVice's GitHub](https://github.com/ScooVice)!

---

**Built with ❤️ for the Discord community. Ready to elevate your server to the next level!** 🚀

#ScooVice-Discord-AI #DiscordBot #v3.0.0 #Archive
