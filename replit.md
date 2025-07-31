# Telegram Channel Management Bot

## Overview

This is a comprehensive Telegram bot built with Python and the `aiogram` framework for automated channel management. The bot provides automated welcome messages, scheduled daily posts, and daily polls for Telegram channels. It supports multi-channel management with individual configuration per channel.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Built on `aiogram` (asynchronous Telegram Bot API framework)
- **Language**: Python 3.8+
- **Architecture Pattern**: Modular design with separate components for handlers, scheduling, configuration, and utilities
- **Storage**: File-based configuration using JSON files
- **Logging**: Comprehensive logging system with file and console output
- **Environment Management**: Uses `python-dotenv` for environment variable management

### Configuration Management
- **Approach**: JSON-based configuration files stored in `/config` directory
- **Structure**: Separate files for channels, messages, and main configuration
- **Hot-reload**: Configuration changes require restart (no hot-reload implemented)

## Key Components

### 1. Main Application (`main.py`)
- Entry point that initializes the bot
- Sets up logging configuration
- Loads environment variables
- Coordinates bot startup and handler setup

### 2. Configuration Manager (`bot/config.py`)
- Manages all configuration files (config.json, channels.json, messages.json)
- Provides default configurations
- Handles configuration directory creation and file loading

### 3. Handlers (`bot/handlers.py`)
- Implements bot command handlers (`/start`, `/help`, `/status`, etc.)
- Manages chat member events for welcome messages
- Implements FSM (Finite State Machine) for poll customization
- Handles admin authentication and permissions

### 4. Scheduler (`bot/scheduler.py`)
- Uses `APScheduler` for automated tasks
- Manages daily message scheduling
- Handles daily poll creation for channels with 500+ subscribers
- Provides cron-based scheduling with configurable times

### 5. Utilities (`bot/utils.py`)
- Admin user verification
- Message formatting functions
- Channel subscriber count retrieval
- Error handling for channel operations

## Data Flow

### Welcome Message Flow
1. User joins/leaves channel → Chat member update event
2. Bot checks if welcome messages are enabled for the channel
3. Formats welcome message with username
4. Sends personalized welcome message

### Daily Messages Flow
1. Scheduler triggers at configured time
2. Bot retrieves list of active channels
3. Selects next message from rotation pool
4. Sends message to all configured channels

### Daily Polls Flow
1. Scheduler triggers at configured time
2. Bot checks subscriber count for each channel
3. Creates poll only for channels with 500+ subscribers
4. Uses configured poll questions and options

### Configuration Flow
1. Bot loads JSON configuration files on startup
2. Admin commands can modify poll settings via FSM
3. Changes are persisted to configuration files

## External Dependencies

### Core Dependencies
- `aiogram`: Telegram Bot API framework
- `python-dotenv`: Environment variable management
- `APScheduler`: Task scheduling system

### Python Standard Library
- `asyncio`: Asynchronous programming
- `logging`: Application logging
- `json`: Configuration file parsing
- `os`: Operating system interface
- `datetime`: Time and date handling

### External Services
- **Telegram Bot API**: Core service for bot functionality
- **Telegram Channels**: Target channels for management

## Deployment Strategy

### Environment Setup
- Requires Python 3.8+ environment
- Virtual environment recommended
- Environment variables stored in `.env` file

### Configuration Requirements
- `BOT_TOKEN`: Telegram bot token (from @BotFather)
- Admin user IDs configured in `config/config.json`
- Bot must have administrator rights on target channels

### File Structure
```
/config/           # Configuration files
  - config.json    # Main configuration
  - channels.json  # Channel definitions
  - messages.json  # Message templates
/bot/             # Bot modules
  - handlers.py   # Command and event handlers
  - scheduler.py  # Automated task management
  - config.py     # Configuration management
  - utils.py      # Utility functions
main.py           # Application entry point
bot.log           # Application logs
```

### Scaling Considerations
- Memory-based FSM storage (not persistent across restarts)
- File-based configuration (suitable for small to medium deployments)
- Single-instance deployment model
- No database dependency (uses JSON files)

### Security Features
- Admin user verification for sensitive commands
- Environment variable protection for bot token
- Error handling for unauthorized channel access
- Logging of all major operations

The bot is designed for straightforward deployment and maintenance, with clear separation of concerns and comprehensive error handling throughout the system.