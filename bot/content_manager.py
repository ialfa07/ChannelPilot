"""
Advanced Content Management Module
Handles scheduled messages, content categories, and personalization
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import random

logger = logging.getLogger(__name__)

@dataclass
class ScheduledMessage:
    """Scheduled message data structure"""
    id: str
    channel_id: str
    content: str
    scheduled_time: str
    category: str
    status: str = "pending"  # pending, sent, cancelled
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class ContentTemplate:
    """Content template data structure"""
    id: str
    name: str
    category: str
    template: str
    variables: List[str]
    usage_count: int = 0

class ContentManager:
    """Manages advanced content features"""
    
    def __init__(self, data_file: str = "content_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
        self.categories = {
            "motivation": "💪 Motivation",
            "news": "📰 Actualités", 
            "tips": "💡 Conseils",
            "entertainment": "🎮 Divertissement",
            "community": "👥 Communauté",
            "announcement": "📢 Annonces"
        }
    
    def _load_data(self) -> Dict[str, Any]:
        """Load content data from file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "scheduled_messages": [],
                "templates": [],
                "content_rotation": {},
                "channel_preferences": {},
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error loading content data: {e}")
            return {"scheduled_messages": [], "templates": [], "content_rotation": {}}
    
    def _save_data(self):
        """Save content data to file"""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving content data: {e}")
    
    def schedule_message(self, channel_id: str, content: str, 
                        scheduled_time: datetime, category: str = "general") -> str:
        """Schedule a message for future delivery"""
        message_id = f"msg_{datetime.now().timestamp():.0f}"
        
        scheduled_msg = ScheduledMessage(
            id=message_id,
            channel_id=channel_id,
            content=content,
            scheduled_time=scheduled_time.isoformat(),
            category=category
        )
        
        self.data["scheduled_messages"].append(asdict(scheduled_msg))
        self._save_data()
        
        logger.info(f"Scheduled message {message_id} for {scheduled_time}")
        return message_id
    
    def get_pending_messages(self, channel_id: Optional[str] = None) -> List[Dict]:
        """Get pending scheduled messages"""
        now = datetime.now()
        pending = []
        
        for msg in self.data["scheduled_messages"]:
            if msg["status"] != "pending":
                continue
                
            scheduled_time = datetime.fromisoformat(msg["scheduled_time"])
            if scheduled_time <= now:
                if not channel_id or msg["channel_id"] == channel_id:
                    pending.append(msg)
        
        return sorted(pending, key=lambda x: x["scheduled_time"])
    
    def mark_message_sent(self, message_id: str):
        """Mark a scheduled message as sent"""
        for msg in self.data["scheduled_messages"]:
            if msg["id"] == message_id:
                msg["status"] = "sent"
                break
        self._save_data()
    
    def create_template(self, name: str, category: str, template: str, 
                       variables: List[str]) -> str:
        """Create a new content template"""
        template_id = f"tpl_{datetime.now().timestamp():.0f}"
        
        content_template = ContentTemplate(
            id=template_id,
            name=name,
            category=category,
            template=template,
            variables=variables
        )
        
        self.data["templates"].append(asdict(content_template))
        self._save_data()
        
        logger.info(f"Created template {name} with ID {template_id}")
        return template_id
    
    def get_templates(self, category: Optional[str] = None) -> List[Dict]:
        """Get content templates, optionally filtered by category"""
        templates = self.data["templates"]
        if category:
            templates = [t for t in templates if t["category"] == category]
        return templates
    
    def use_template(self, template_id: str, variables: Dict[str, str]) -> str:
        """Use a template to generate content"""
        template = None
        for t in self.data["templates"]:
            if t["id"] == template_id:
                template = t
                break
        
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        content = template["template"]
        for var, value in variables.items():
            content = content.replace(f"{{{var}}}", value)
        
        # Update usage count
        template["usage_count"] += 1
        self._save_data()
        
        return content
    
    def set_channel_preferences(self, channel_id: str, preferences: Dict[str, Any]):
        """Set content preferences for a channel"""
        self.data["channel_preferences"][channel_id] = {
            **preferences,
            "updated_at": datetime.now().isoformat()
        }
        self._save_data()
    
    def get_channel_preferences(self, channel_id: str) -> Dict[str, Any]:
        """Get content preferences for a channel"""
        return self.data["channel_preferences"].get(channel_id, {
            "preferred_categories": ["motivation", "community"],
            "post_frequency": "daily",
            "best_times": ["09:00", "18:00"],
            "language": "fr",
            "tone": "friendly"
        })
    
    def get_rotated_content(self, channel_id: str, category: str) -> Optional[str]:
        """Get content using rotation algorithm"""
        rotation_key = f"{channel_id}_{category}"
        
        # Get available content for category
        templates = self.get_templates(category)
        if not templates:
            return None
        
        # Initialize rotation if needed
        if rotation_key not in self.data["content_rotation"]:
            self.data["content_rotation"][rotation_key] = {
                "used_templates": [],
                "last_reset": datetime.now().isoformat()
            }
        
        rotation = self.data["content_rotation"][rotation_key]
        
        # Reset rotation if all templates used
        available = [t for t in templates if t["id"] not in rotation["used_templates"]]
        if not available:
            rotation["used_templates"] = []
            rotation["last_reset"] = datetime.now().isoformat()
            available = templates
        
        # Select template with weighted randomization (less used templates preferred)
        weights = [1 / (t["usage_count"] + 1) for t in available]
        selected = random.choices(available, weights=weights)[0]
        
        # Mark as used
        rotation["used_templates"].append(selected["id"])
        self._save_data()
        
        return selected["template"]
    
    def get_content_by_event(self, event_type: str, channel_id: str) -> Optional[str]:
        """Get content based on events (holidays, anniversaries, etc.)"""
        today = datetime.now()
        
        # Check for special dates
        special_content = {
            "01-01": "🎉 Bonne année ! Que cette nouvelle année soit remplie de succès !",
            "12-25": "🎄 Joyeux Noël ! Passez de merveilleuses fêtes !",
            "07-14": "🇫🇷 Bonne fête nationale française !",
            "05-01": "🌸 Bonne fête du travail !",
            "valentine": "💝 Joyeuse Saint-Valentin !",
        }
        
        date_key = today.strftime("%m-%d")
        if date_key in special_content:
            return special_content[date_key]
        
        # Check for day of week patterns
        weekday = today.weekday()
        if weekday == 0:  # Monday
            return "💪 Nouvelle semaine, nouveaux défis ! Bonne semaine à tous !"
        elif weekday == 4:  # Friday
            return "🎉 Bon weekend à tous ! Profitez bien de vos moments de repos !"
        
        return None
    
    def generate_content_calendar(self, channel_id: str, days: int = 7) -> List[Dict]:
        """Generate content calendar for specified period"""
        calendar = []
        preferences = self.get_channel_preferences(channel_id)
        start_date = datetime.now()
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            
            # Check for events
            event_content = self.get_content_by_event("daily", channel_id)
            
            # Get category for the day
            categories = preferences.get("preferred_categories", ["motivation", "community"])
            category = categories[i % len(categories)]
            
            calendar_entry = {
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A"),
                "category": category,
                "suggested_times": preferences.get("best_times", ["09:00"]),
                "event_content": event_content,
                "templates_available": len(self.get_templates(category))
            }
            
            calendar.append(calendar_entry)
        
        return calendar

# Global content manager instance
content_manager = ContentManager()