# Changelog

All notable changes to **ScooVice-Discord-AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

Maintenance has resumed since the v3.0.0 archive notice.

### Fixed

- Temporary bans are stored in SQLite and are resumed after bot restarts.
- AI requests use Groq's asynchronous client and keep separate in-memory
  conversations for each user and server.
- AutoMod no longer blocks sample placeholder words or all links by default;
  optional rules can be configured through environment variables.
- Updated the Groq SDK dependency and corrected setup and feature documentation.

## [v3.0.0] - 2026-01-08 🚀 **FINAL RELEASE - PROJECT ARCHIVE**

### 🎉 **The Ultimate Discord Bot - Complete Feature Set**

#### ✨ **New Features**

- **🤖 AI Chatbot**: Advanced conversational AI powered by Groq

  - `/chat <message>` - Natural language conversations
  - `/clear_chat` - Reset conversation history
  - Context-aware responses with conversation memory

- **🌍 Enhanced Multi-Language Support**: 9 languages total

  - Added: Spanish, French, German, Portuguese, Russian, Japanese, Korean, Chinese
  - Per-server and per-user language preferences
  - Full command translations and localized responses

#### 🔧 **Technical Improvements**

- **New Dependencies**: Added groq
- **AI Integration**: Groq API client with conversation management

#### 🎨 **User Experience**

- **Updated Branding**: Renamed to ScooVice-Discord-AI
- **Enhanced Help**: Comprehensive command documentation
- **Improved Presence**: Updated status message

#### ❌ **Remove Features**

- **Remove Database**
- **Remove Warning System**

### 📈 **Progress**: **100% Complete - Final Release**

**This is the final version of ScooVice-Discord-AI. The project will now be archived.**

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
