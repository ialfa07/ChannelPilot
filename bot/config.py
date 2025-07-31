"""
Configuration management for the bot
"""

import json
import logging
import os
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the bot"""
    
    def __init__(self):
        self.config_dir = "config"
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.channels_file = os.path.join(self.config_dir, "channels.json")
        self.messages_file = os.path.join(self.config_dir, "messages.json")
        
        self._ensure_config_directory()
        self._load_configurations()
    
    def _ensure_config_directory(self):
        """Ensure configuration directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            logger.info(f"Created configuration directory: {self.config_dir}")
    
    def _load_configurations(self):
        """Load all configuration files"""
        try:
            # Load main config
            self.config = self._load_json_file(self.config_file, self._get_default_config())
            
            # Load channels
            self.channels = self._load_json_file(self.channels_file, {})
            
            # Load messages
            self.messages = self._load_json_file(self.messages_file, self._get_default_messages())
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def _load_json_file(self, filepath: str, default_data: Dict) -> Dict:
        """Load JSON file with default fallback"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create file with default data
                self._save_json_file(filepath, default_data)
                return default_data
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return default_data
    
    def _save_json_file(self, filepath: str, data: Dict):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved configuration to {filepath}")
        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "timezone": "Europe/Paris",
            "admin_users": [],
            "daily_messages": {
                "enabled": True,
                "hour": 9,
                "minute": 0
            },
            "polls": {
                "enabled": True,
                "hour": 10,
                "minute": 0,
                "question": "Comment vous sentez-vous aujourd'hui ?",
                "min_subscribers": 500,
                "options": [
                    "Motivé 💪",
                    "Fatigué 😴",
                    "Neutre 😐"
                ]
            }
        }
    
    def _get_default_messages(self) -> Dict:
        """Get default messages"""
        return {
            "welcome_message": "Bienvenue, {username} ! Merci de nous avoir rejoints 🎉",
            "daily_messages": [
                "Nouveau jour, nouvelle énergie ! 🔥 Passez une excellente journée !",
                "Bonjour ! 🌅 Que cette journée vous apporte de belles surprises !",
                "Bonne journée à tous ! 💪 Restons motivés ensemble !",
                "Salut la communauté ! ☀️ Une nouvelle journée pleine de possibilités !",
                "Hello ! 🚀 Prêts à conquérir cette journée ?",
                "Bonjour ! 🌟 Ensemble, nous sommes plus forts !",
                "Bonne journée ! 🎯 Fixons-nous de beaux objectifs aujourd'hui !"
            ]
        }
    
    def get_admin_users(self) -> List[int]:
        """Get list of admin user IDs"""
        return self.config.get("admin_users", [])
    
    def get_channels(self) -> Dict[str, Dict]:
        """Get configured channels"""
        return self.channels
    
    def get_welcome_message(self) -> str:
        """Get welcome message template"""
        return self.messages.get("welcome_message", "Bienvenue, {username} ! 🎉")
    
    def get_daily_messages(self) -> List[str]:
        """Get daily messages list"""
        return self.messages.get("daily_messages", [])
    
    def get_daily_message_config(self) -> Dict:
        """Get daily message configuration"""
        return self.config.get("daily_messages", {})
    
    def get_poll_config(self) -> Dict:
        """Get poll configuration"""
        return self.config.get("polls", {})
    
    def get_poll_options(self) -> List[str]:
        """Get poll options"""
        return self.config.get("polls", {}).get("options", [])
    
    def get_timezone(self) -> str:
        """Get configured timezone"""
        return self.config.get("timezone", "Europe/Paris")
    
    def update_poll_options(self, options: List[str]):
        """Update poll options"""
        try:
            if "polls" not in self.config:
                self.config["polls"] = {}
            
            self.config["polls"]["options"] = options
            self._save_json_file(self.config_file, self.config)
            logger.info(f"Updated poll options: {options}")
            
        except Exception as e:
            logger.error(f"Error updating poll options: {e}")
    
    def add_admin_user(self, user_id: int):
        """Add admin user"""
        try:
            if user_id not in self.config.get("admin_users", []):
                if "admin_users" not in self.config:
                    self.config["admin_users"] = []
                self.config["admin_users"].append(user_id)
                self._save_json_file(self.config_file, self.config)
                logger.info(f"Added admin user: {user_id}")
        except Exception as e:
            logger.error(f"Error adding admin user: {e}")
    
    def add_channel(self, channel_id: str, channel_info: Dict):
        """Add channel to configuration"""
        try:
            self.channels[channel_id] = channel_info
            self._save_json_file(self.channels_file, self.channels)
            logger.info(f"Added channel: {channel_id}")
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
    
    def remove_channel(self, channel_id: str):
        """Remove channel from configuration"""
        try:
            if channel_id in self.channels:
                del self.channels[channel_id]
                self._save_json_file(self.channels_file, self.channels)
                logger.info(f"Removed channel: {channel_id}")
        except Exception as e:
            logger.error(f"Error removing channel: {e}")
    
    def update_channel_status(self, channel_id: str, active: bool):
        """Update channel active status"""
        try:
            if channel_id in self.channels:
                self.channels[channel_id]["active"] = active
                self._save_json_file(self.channels_file, self.channels)
                logger.info(f"Updated channel {channel_id} status: {active}")
        except Exception as e:
            logger.error(f"Error updating channel status: {e}")
    
    def reload_configuration(self):
        """Reload all configuration files"""
        try:
            self._load_configurations()
            logger.info("Configuration reloaded")
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
