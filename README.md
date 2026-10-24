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

ScooVice Discord AI brings everyday moderation tools, mention-based AI chat,
and one-click voice controls into one Python-powered Discord bot. It keeps
temporary ban schedules and server AI settings across restarts.

## Features

| Area | What it does |
| --- | --- |
| AI chat | Mention the bot in a server or send it a DM. Recent context is kept separately for each user in each server. |
| Interactive controls | `/settings` opens server AI settings and `/voice` opens join/leave buttons. |
| Temporary bans | `/tempban` stores expiry times in SQLite and resumes the schedule after a restart. |
| Moderation | Permission-checked commands for kicking, banning, unbanning, and applying or removing Discord timeouts. |
| AutoMod | Detects message bursts; optional whole-word filtering, link blocking, and excessive-caps checks are configurable. |
| Server logs | Posts ban, unban, and timeout events to a `#mod-logs` text channel when one exists. |
| Helpful responses | Shared embeds, a `/help` command, and clear feedback when command permissions are missing. |

### A few important details

- Chat history is held in memory and is cleared when the bot restarts. Server
  AI settings persist in `data/ai-settings.sqlite3`.
- The voice panel joins the user's current channel silently and can disconnect
  the bot. It does not play music or transmit generated speech.
- AutoMod checks spam by default. Banned words, link blocking, and caps
  filtering are opt-in so a fresh install does not remove ordinary messages.
- Groq's free tier has usage and rate limits; it is not unlimited. Check your
  account's current limits in the Groq Console.
- Keep the `data/` directory on persistent storage if the bot is hosted. It
  contains the SQLite database used for temporary-ban schedules.

## Commands

| Command | Purpose | Required server permission |
| --- | --- | --- |
| `@Bot <message>` | Chat with the configured Groq model in a server. | None |
| Direct message | Chat privately with the bot. | None |
| `/clear_chat` | Clear your AI conversation in this server or DM. | None |
| `/settings` | Configure reasoning, output token cap, and history length. | Manage Server |
| `/voice` | Open buttons to join your voice channel or leave voice. | None |
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
ensure `data/` is persisted by your host. Startup output is intentionally
minimal; errors and warnings are still logged.

## Configuration

`.env.example` documents every supported setting:

| Variable | Default | Description |
| --- | --- | --- |
| `DISCORD_TOKEN` | Required | Discord bot token. |
| `GROQ_API_KEY` | Required | Groq API key. |
| `GROQ_MODEL` | `openai/gpt-oss-20b` | Active model ID available to your Groq account. |
| `GROQ_REASONING_EFFORT` | `low` | Default reasoning effort (`low`, `medium`, `high`). |
| `GROQ_MAX_COMPLETION_TOKENS` | `512` | Default output budget (`256`, `512`, `1024`, `2048`). |
| `GROQ_HISTORY_TURNS` | `5` | Default number of previous chat turns to include (`2`, `5`, `10`). |
| `AUTOMOD_BANNED_WORDS` | Empty | Comma-separated whole words to block, matched case-insensitively. |
| `AUTOMOD_BLOCK_LINKS` | `false` | Set to `true` to remove messages containing web links. |
| `AUTOMOD_BLOCK_EXCESSIVE_CAPS` | `false` | Set to `true` to remove messages with excessive uppercase letters. |

Example:

```env
DISCORD_TOKEN=your_discord_token
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
GROQ_REASONING_EFFORT=low
GROQ_MAX_COMPLETION_TOKENS=512
GROQ_HISTORY_TURNS=5
AUTOMOD_BANNED_WORDS=exampleword,anotherword
AUTOMOD_BLOCK_LINKS=false
AUTOMOD_BLOCK_EXCESSIVE_CAPS=false
```

AutoMod's spam rule removes a user's sixth message within a rolling
10-second window. Members with **Manage Messages** are exempt. Deleted
messages and warning embeds require the bot to have **Manage Messages**,
**Send Messages**, and **Embed Links** in that channel.

### Configure AI from Discord

Run `/settings` in a server as someone with **Manage Server**. The private
settings panel lets server managers change:

- **Reasoning effort:** low (quickest), medium, or high.
- **Maximum completion tokens:** 256, 512, 1,024, or 2,048. This is a ceiling,
  not a promise that every response will use the full amount.
- **Chat history:** keep 2, 5, or 10 previous turns as context.

The **Reset defaults** button restores the values from `.env`. The model ID
itself is still selected with `GROQ_MODEL`. Usage shown on each AI response
reports input and output tokens returned by Groq (and reasoning tokens when
the API supplies that detail). Higher reasoning effort, longer context, and
larger output limits can increase latency and consume more of your Groq
account's quota. There is no bot-imposed chat cooldown; Groq's own rate limits
still apply.

### Voice controls

Run `/voice`, connect to your voice channel, and press **Join my voice**. The
bot joins deafened and silent. Press **Leave voice** to disconnect. Moving the
bot out of a different voice channel is restricted to server managers. The
bot needs **Connect** permission in the destination channel. Voice audio
playback and voice-based AI conversations are not currently implemented.

## Development

Install dependencies, then run the focused test suite:

```bash
python -m unittest discover -s tests -v
python -m compileall -q bot tests
```

Tests cover mention-based AI request settings and conversation isolation,
durable temporary-ban schedules, moderation role checks, AutoMod behavior,
Discord error responses, settings persistence and access checks, and mocked
voice join/leave controls.

## Project status

This repository was previously marked archived. Maintenance has resumed for
the updates documented in the changelog. The project is maintained as a
community bot rather than a hosted service; operators are responsible for
keeping secrets safe, enabling required Discord intents, and preserving the
bot's data directory.

## License

Released under the [GNU General Public License v3.0](LICENSE).
