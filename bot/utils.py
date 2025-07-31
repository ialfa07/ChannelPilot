"""
Utility functions for the bot
"""

import logging
from typing import Optional
from aiogram import Bot

from .config import Config

logger = logging.getLogger(__name__)

async def is_admin(user_id: int, config: Config) -> bool:
    """Check if user is admin"""
    admin_users = config.get_admin_users()
    return user_id in admin_users

def format_welcome_message(template: str, username: str) -> str:
    """Format welcome message with username"""
    try:
        # Add @ prefix if not present and not empty
        if username and not username.startswith('@'):
            username = f"@{username}"
        elif not username:
            username = "Nouvel abonné"
        
        return template.format(username=username)
    except Exception as e:
        logger.error(f"Error formatting welcome message: {e}")
        return f"Bienvenue, {username} ! 🎉"

async def get_channel_subscriber_count(bot: Bot, channel_id: str) -> int:
    """Get channel subscriber count"""
    try:
        chat = await bot.get_chat(channel_id)
        
        # For channels, we need to use get_chat_member_count
        try:
            count = await bot.get_chat_member_count(channel_id)
            return count
        except:
            # Fallback: approximate count (not exact for large channels)
            return getattr(chat, 'member_count', 0)
            
    except Exception as e:
        logger.error(f"Error getting subscriber count for {channel_id}: {e}")
        return 0

async def send_message_to_channel(bot: Bot, channel_id: str, message: str, parse_mode: str = "Markdown") -> bool:
    """Send message to channel with error handling"""
    try:
        await bot.send_message(
            chat_id=channel_id,
            text=message,
            parse_mode=parse_mode
        )
        return True
    except Exception as e:
        logger.error(f"Error sending message to {channel_id}: {e}")
        return False

async def send_poll_to_channel(bot: Bot, channel_id: str, question: str, options: list) -> bool:
    """Send poll to channel with error handling"""
    try:
        await bot.send_poll(
            chat_id=channel_id,
            question=question,
            options=options,
            is_anonymous=True,
            allows_multiple_answers=False
        )
        return True
    except Exception as e:
        logger.error(f"Error sending poll to {channel_id}: {e}")
        return False

def validate_channel_id(channel_id: str) -> bool:
    """Validate channel ID format"""
    try:
        # Channel IDs should start with - and be numeric
        if not channel_id.startswith('-'):
            return False
        
        # Try to convert to int (excluding the - prefix)
        int(channel_id[1:])
        return True
        
    except (ValueError, TypeError):
        return False

def format_time(hour: int, minute: int) -> str:
    """Format time in HH:MM format"""
    return f"{hour:02d}:{minute:02d}"

def parse_time(time_str: str) -> tuple:
    """Parse time string to hour and minute"""
    try:
        parts = time_str.split(':')
        if len(parts) != 2:
            raise ValueError("Invalid time format")
        
        hour = int(parts[0])
        minute = int(parts[1])
        
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            raise ValueError("Invalid time values")
        
        return hour, minute
        
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing time '{time_str}': {e}")
        raise ValueError("Time format should be HH:MM")

def sanitize_username(username: str) -> str:
    """Sanitize username for display"""
    if not username:
        return "Utilisateur"
    
    # Remove @ if present
    username = username.replace('@', '')
    
    # Limit length
    if len(username) > 50:
        username = username[:47] + "..."
    
    return username

def get_user_display_name(user) -> str:
    """Get user display name from user object"""
    if hasattr(user, 'username') and user.username:
        return f"@{user.username}"
    elif hasattr(user, 'first_name') and user.first_name:
        name = user.first_name
        if hasattr(user, 'last_name') and user.last_name:
            name += f" {user.last_name}"
        return name
    else:
        return "Utilisateur"
