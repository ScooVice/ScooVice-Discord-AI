# Changelog

All notable changes to **ScooVice-Discord-AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v3.1.0] - 2026-10-24

### Added

- Mention/DM-based AI chat.
- A private `/settings` panel with buttons and dropdowns for reasoning effort,
  completion token cap, and chat history length.
- A `/voice` panel with buttons to join a user's voice channel or disconnect.
- Groq token-usage details on AI replies and tests for the interactive controls.
- Updated all direct Python dependencies to their latest stable releases.

### Changed

- Default reasoning effort is `low`; server managers can tune it from Discord.
- Added a styled terminal startup banner with bot, server, command, and voice status.
- Updated Discord voice support for the current DAVE protocol and its required packages.
- Updated PyNaCl to `1.6.2`, resolving two advisories affecting the older voice dependency.
- Applied a consistent visual style to bot embeds.
- Refreshed setup, feature, configuration, dependency, and voice documentation.

### Fixed

- The `/help` guide now reflects the current mention-based AI chat and commands.
- Voice controls acknowledge interactions before connecting, avoiding expired-button responses.
- Voice connection failures now identify permission, timeout, and dependency issues.
- Updated PyNaCl to `1.6.2`, resolving two advisories affecting the older voice dependency.
- AI replies report API usage and keep configured context lengths.
- Mention-based AI messages are excluded from AutoMod spam counting.

## [V3.0.0] - 2026-01-08

This release was originally announced as the final release. Active maintenance
resumed in 3.1.0.

### Added

- Groq-powered AI chat with conversation memory and a command to clear history.
- Expanded language support.

### Changed

 - Updated project branding and help documentation.
 - Removed the warning system and database used by the previous implementation.

---

## [v2.0.0] - 2025-12-19 🚀 **MAJOR RELEASE**

### 🎉 **Complete Overhaul - Production Ready Moderation Bot**

#### ✨ **New Features**

- **Full Moderation Suite**: Comprehensive admin commands (/kick, /ban, /tempban, /mute, /unmute)
- **Auto-Moderation System**: Intelligent detection of banned words, excessive caps, links, and spam
- **Advanced Warning System**: Automatic timeout after 3 warnings with reset mechanism
- **Role Hierarchy Protection**: Prevents moderators from targeting higher roles
- **Multi-Language Support**: Basic i18n for English and Indonesian
- **Modern Slash Commands**: All interactions use Discord's latest slash command system
- **Professional Embeds**: Beautiful, consistent embed responses with branding

#### 🔧 **Technical Improvements**

- **Error Handling**: Global slash command error handler for all permission and check failures
- **Timeout Prevention**: All commands use defer/followup pattern for instant responses
- **Stable Sync**: Global command synchronization to prevent duplicates
- **Async Architecture**: Fully asynchronous codebase for optimal performance
- **Environment Configuration**: Secure token management with .env files

#### 🛡️ **Security & Safety**

- **Permission Checks**: Comprehensive permission validation on all commands
- **Hierarchy Validation**: Role-based access control
- **Input Validation**: Proper error handling for invalid inputs

#### 🎨 **User Experience**

- **Instant Responses**: No more "thinking" timeouts
- **Clear Error Messages**: User-friendly error embeds
- **Ephemeral Errors**: Private error notifications
- **Professional Appearance**: Consistent branding and styling

### 📈 **Progress**: **100% Complete - Launch Ready**

---

## [v0.1.1-day2] - 2025-12-17

### Added

- Admin moderation commands:
  - `/kick` with permission checks
  - `/ban` with optional message deletion
  - `/unban` for unbanning users
- Role hierarchy validation to prevent abuse
- DM notifications sent to affected users
- Moderation logging system

### Improved

- Permission error handling for admin commands
- Clearer and more user-friendly error messages
- Beautiful embed responses for moderation actions

### Technical

- Helper functions for moderation logging
- Centralized admin command error handlers

📊 Progress: **5 / 7 features complete (71%)**

---

## [v0.1.0-day1] - 2025-12-16

### Added

- Initial project setup for ScooVice BOT V2
- Slash command system foundation
- AI chat powered by Groq (Llama 3.3 70B)
- Natural chat support (tag, reply, and DM)
- Embed-based response system

### Setup

- Project structure and scripting
- Environment configuration (`.env`, `.env.example`)
- Dependency management (`requirements.txt`)
- Documentation files (`README.md`, `LICENSE`)

### Performance

- Early-stage speed optimizations
- Clean and scalable codebase foundation

📊 Progress: **4 / 7 features complete (57%)**
