# ScooVice-Discord-AI

A Discord bot with moderation commands, configurable AutoMod, and AI chat
powered by Groq.

## Features

- Moderation slash commands: `/kick`, `/ban`, `/tempban`, `/unban`, `/mute`,
  and `/unmute`.
- `/tempban` schedules unbanning in a local SQLite database, so its schedule
  survives bot restarts. Keep the `data` directory on persistent storage.
- `/chat` uses the Groq model configured by `GROQ_MODEL` and keeps up to 20
  recent messages per user and server in memory. `/clear_chat` clears that
  history. Chat history is not persisted across restarts.
- AutoMod's spam check removes a user's sixth message within 10 seconds.
  Banned-word, link, and excessive-caps checks are configurable and disabled
  unless enabled in `.env`.
- `/help` and `/ping`.

## Requirements

- Python 3.10 or newer
- A Discord bot token
- A Groq API key

The Groq free plan has usage and rate limits; it is not unlimited. Check your
Groq account for its current limits.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in `DISCORD_TOKEN` and
   `GROQ_API_KEY`. `GROQ_MODEL` defaults to `openai/gpt-oss-20b`.

3. Optionally configure AutoMod in `.env`:

   ```env
   AUTOMOD_BANNED_WORDS=word1,word2
   AUTOMOD_BLOCK_LINKS=false
   AUTOMOD_BLOCK_EXCESSIVE_CAPS=false
   ```

   Banned words are matched as whole words, case-insensitively. Set link or
   caps checks to `true` only if you want those rules enabled. Spam detection
   is enabled by default. The bot needs **Manage Messages**, **Send Messages**,
   and **Embed Links** permissions, and the Message Content intent enabled in
   the Discord Developer Portal for AutoMod to work.

4. Start the bot:

   ```bash
   python run.py
   ```

Invite the bot with the `bot` and `applications.commands` OAuth2 scopes, and
grant only the permissions it needs for the commands you plan to use.

## Commands

- `/chat <message>` and `/clear_chat`
- `/kick <member> [reason]`, `/ban <member> [reason]`, `/unban <user_id>`
- `/tempban <member> <days> [reason]` (minimum one day)
- `/mute <member> <minutes> [reason]` and `/unmute <member> [reason]`
- `/help` and `/ping`
