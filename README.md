<div align="center">

# ScooVice Discord AI

**A practical Discord companion for AI chat and server moderation.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.4.0-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Groq SDK](https://img.shields.io/badge/Groq%20SDK-1.7.0-F55036)](https://pypi.org/project/groq/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

[Features](#features) · [Commands](#commands) · [Setup](#getting-started) · [Configuration](#configuration) · [Roadmap](#project-status)

</div>

---

ScooVice Discord AI brings everyday moderation tools and conversational AI
into one Python-powered Discord bot. It uses slash commands, keeps temporary
ban schedules across restarts, and connects to Groq using a model you can
change through configuration.

## Features

| Area | What it does |
| --- | --- |
| AI chat | `/chat` talks to the Groq model in `.env`; recent context is kept separately for each user in each server. |
| Temporary bans | `/tempban` stores expiry times in SQLite and resumes the schedule after a restart. |
| Moderation | Permission-checked commands for kicking, banning, unbanning, and applying or removing Discord timeouts. |
| AutoMod | Detects message bursts; optional whole-word filtering, link blocking, and excessive-caps checks are configurable. |
| Server logs | Posts ban, unban, and timeout events to a `#mod-logs` text channel when one exists. |
| Helpful responses | Shared embeds, a `/help` command, and clear feedback when command permissions are missing. |

### A few important details

- Chat history is held in memory and is cleared when the bot restarts. The
  cache is capped to avoid unbounded growth.
- AutoMod checks spam by default. Banned words, link blocking, and caps
  filtering are opt-in so a fresh install does not remove ordinary messages.
- Groq's free tier has usage and rate limits; it is not unlimited. Check your
  account's current limits in the Groq Console.
- Keep the `data/` directory on persistent storage if the bot is hosted. It
  contains the SQLite database used for temporary-ban schedules.

## Commands

| Command | Purpose | Required server permission |
| --- | --- | --- |
| `/chat <message>` | Chat with the configured Groq model. | None |
| `/clear_chat` | Clear your AI conversation in this server or DM. | None |
| `/kick <member> [reason]` | Remove a member from the server. | Kick Members |
| `/ban <member> [reason]` | Permanently ban a member. | Ban Members |
| `/tempban <member> <days> [reason]` | Ban for 1–36,500 days; expiry survives restarts. | Ban Members |
| `/unban <user_id> [reason]` | Unban a Discord user by ID. | Ban Members |
| `/mute <member> <minutes> [reason]` | Apply a Discord timeout for 1–40,320 minutes. | Moderate Members |
| `/unmute <member> [reason]` | Remove a Discord timeout. | Moderate Members |
| `/ping` | Show the bot's WebSocket latency. | None |
| `/help` | Show the command list in Discord. | None |

Moderation actions also respect the bot's role position and the invoking
moderator's role position. The server owner can moderate members regardless
of role position, subject to the bot's own role and permissions.

## Getting started

### 1. Create the Discord application

Create an application in the
[Discord Developer Portal](https://discord.com/developers/applications), add a
bot, and copy its token. Enable **Message Content Intent** and **Server Members
Intent** under *Bot → Privileged Gateway Intents*.

Invite the bot using the `bot` and `applications.commands` OAuth2 scopes.
Grant the permissions for the commands you plan to use:

- View Channels and Send Messages
- Embed Links
- Manage Messages (AutoMod)
- Kick Members, Ban Members, and Moderate Members (moderation commands)

Place the bot's role above the roles it needs to moderate.

### 2. Get a Groq API key

Create an API key in the [Groq Console](https://console.groq.com/). The bot
uses the Groq API; free-plan availability and rate limits are controlled by
Groq and can change.

### 3. Install and configure

Python 3.10 or newer is required. From the repository directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux, create and activate the virtual environment with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and enter your Discord token and Groq API key. Never commit this
file or share either secret.

### 4. Run the bot

```bash
python run.py
```

The bot loads its slash commands at startup. Keep the process running and
ensure `data/` is persisted by your host.

## Configuration

`.env.example` documents every supported setting:

| Variable | Default | Description |
| --- | --- | --- |
| `DISCORD_TOKEN` | Required | Discord bot token. |
| `GROQ_API_KEY` | Required | Groq API key. |
| `GROQ_MODEL` | `openai/gpt-oss-20b` | Active model ID available to your Groq account. |
| `AUTOMOD_BANNED_WORDS` | Empty | Comma-separated whole words to block, matched case-insensitively. |
| `AUTOMOD_BLOCK_LINKS` | `false` | Set to `true` to remove messages containing web links. |
| `AUTOMOD_BLOCK_EXCESSIVE_CAPS` | `false` | Set to `true` to remove messages with excessive uppercase letters. |

Example:

```env
DISCORD_TOKEN=your_discord_token
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
AUTOMOD_BANNED_WORDS=exampleword,anotherword
AUTOMOD_BLOCK_LINKS=false
AUTOMOD_BLOCK_EXCESSIVE_CAPS=false
```

AutoMod's spam rule removes a user's sixth message within a rolling
10-second window. Members with **Manage Messages** are exempt. Deleted
messages and warning embeds require the bot to have **Manage Messages**,
**Send Messages**, and **Embed Links** in that channel.

## Development

Install dependencies, then run the focused test suite:

```bash
python -m unittest discover -s tests -v
python -m compileall -q bot tests
```

Tests cover AI model selection and conversation isolation, durable temporary
ban schedules, moderation role checks, AutoMod behavior, and Discord error
responses.

## Project status

This repository was previously marked archived. Maintenance has resumed for
the updates documented in the changelog. The project is maintained as a
community bot rather than a hosted service; operators are responsible for
keeping secrets safe, enabling required Discord intents, and preserving the
bot's data directory.

## License

Released under the [GNU General Public License v3.0](LICENSE).
