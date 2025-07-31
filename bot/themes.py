"""
Theme and Personalization Module
Handles message styling, templates, and visual customization
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class MessageTheme:
    """Message theme configuration"""
    name: str
    primary_emoji: str
    secondary_emoji: str
    colors: Dict[str, str]  # For future HTML/rich text support
    header_style: str
    footer_style: str
    separator: str
    bullet_point: str

class ThemeManager:
    """Manages themes and message styling"""
    
    def __init__(self, themes_file: str = "themes.json"):
        self.themes_file = themes_file
        self.themes = self._load_themes()
        self.signatures = self._load_signatures()
    
    def _load_themes(self) -> Dict[str, MessageTheme]:
        """Load themes from file"""
        try:
            with open(self.themes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                themes = {}
                for name, theme_data in data.get("themes", {}).items():
                    themes[name] = MessageTheme(**theme_data)
                return themes
        except FileNotFoundError:
            return self._create_default_themes()
        except Exception as e:
            logger.error(f"Error loading themes: {e}")
            return self._create_default_themes()
    
    def _create_default_themes(self) -> Dict[str, MessageTheme]:
        """Create default themes"""
        themes = {
            "default": MessageTheme(
                name="Default",
                primary_emoji="🤖",
                secondary_emoji="✨",
                colors={"primary": "#0088cc", "secondary": "#17a2b8"},
                header_style="**{title}**",
                footer_style="_Envoyé par {bot_name}_",
                separator="─" * 20,
                bullet_point="•"
            ),
            "motivational": MessageTheme(
                name="Motivational",
                primary_emoji="💪",
                secondary_emoji="🔥",
                colors={"primary": "#ff6b35", "secondary": "#f7931e"},
                header_style="🌟 **{title}** 🌟",
                footer_style="💫 _Continuez à briller !_",
                separator="🔥" * 10,
                bullet_point="⚡"
            ),
            "professional": MessageTheme(
                name="Professional",
                primary_emoji="📊",
                secondary_emoji="💼",
                colors={"primary": "#2c3e50", "secondary": "#34495e"},
                header_style="📋 **{title}**",
                footer_style="🏢 _{channel_name}_",
                separator="▪" * 15,
                bullet_point="▪"
            ),
            "gaming": MessageTheme(
                name="Gaming",
                primary_emoji="🎮",
                secondary_emoji="🕹️",
                colors={"primary": "#9b59b6", "secondary": "#8e44ad"},
                header_style="🎯 **{title}** 🎯",
                footer_style="🎮 _Game On!_",
                separator="⚡" * 8,
                bullet_point="🔸"
            ),
            "community": MessageTheme(
                name="Community",
                primary_emoji="👥",
                secondary_emoji="🤝",
                colors={"primary": "#27ae60", "secondary": "#2ecc71"},
                header_style="🌍 **{title}** 🌍",
                footer_style="💚 _Ensemble, nous sommes plus forts_",
                separator="🌟" * 6,
                bullet_point="🔹"
            )
        }
        self._save_themes(themes)
        return themes
    
    def _save_themes(self, themes: Dict[str, MessageTheme]):
        """Save themes to file"""
        try:
            data = {
                "themes": {name: asdict(theme) for name, theme in themes.items()},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.themes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving themes: {e}")
    
    def _load_signatures(self) -> Dict[str, str]:
        """Load channel signatures"""
        try:
            with open("signatures.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            default_sigs = {
                "default": "📱 Votre Bot Telegram",
                "motivational": "💪 Restons motivés ensemble !",
                "professional": "📊 Information professionnelle",
                "gaming": "🎮 Gaming Community",
                "community": "👥 Notre communauté"
            }
            self._save_signatures(default_sigs)
            return default_sigs
    
    def _save_signatures(self, signatures: Dict[str, str]):
        """Save signatures to file"""
        try:
            with open("signatures.json", 'w', encoding='utf-8') as f:
                json.dump(signatures, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving signatures: {e}")
    
    def apply_theme(self, content: str, theme_name: str = "default", 
                   title: str = "", variables: Dict[str, str] = None) -> str:
        """Apply theme styling to message content"""
        theme = self.themes.get(theme_name, self.themes["default"])
        if variables is None:
            variables = {}
        
        formatted_content = content
        
        # Apply header if title provided
        if title:
            header = theme.header_style.format(title=title)
            formatted_content = f"{theme.primary_emoji} {header}\n\n{formatted_content}"
        
        # Replace bullet points
        if theme.bullet_point != "•":
            formatted_content = formatted_content.replace("•", theme.bullet_point)
        
        # Add separator if content is long
        if len(formatted_content) > 200:
            parts = formatted_content.split('\n\n')
            if len(parts) > 1:
                separator = f"\n{theme.separator}\n"
                formatted_content = separator.join(parts)
        
        # Apply footer
        footer_vars = {
            "bot_name": variables.get("bot_name", "Link Center Bot"),
            "channel_name": variables.get("channel_name", ""),
            **variables
        }
        
        if any(var in theme.footer_style for var in footer_vars.keys()):
            footer = theme.footer_style.format(**footer_vars)
            formatted_content = f"{formatted_content}\n\n{footer}"
        
        # Add secondary emoji for emphasis
        if theme.secondary_emoji:
            # Add to end of content
            formatted_content = f"{formatted_content} {theme.secondary_emoji}"
        
        return formatted_content
    
    def create_custom_theme(self, name: str, config: Dict[str, Any]) -> bool:
        """Create a custom theme"""
        try:
            theme = MessageTheme(
                name=config.get("name", name),
                primary_emoji=config.get("primary_emoji", "🤖"),
                secondary_emoji=config.get("secondary_emoji", "✨"),
                colors=config.get("colors", {"primary": "#0088cc", "secondary": "#17a2b8"}),
                header_style=config.get("header_style", "**{title}**"),
                footer_style=config.get("footer_style", "_Envoyé par {bot_name}_"),
                separator=config.get("separator", "─" * 20),
                bullet_point=config.get("bullet_point", "•")
            )
            
            self.themes[name] = theme
            self._save_themes(self.themes)
            logger.info(f"Created custom theme: {name}")
            return True
        except Exception as e:
            logger.error(f"Error creating theme {name}: {e}")
            return False
    
    def get_theme_preview(self, theme_name: str) -> str:
        """Generate a preview of a theme"""
        sample_content = """Voici un exemple de message avec ce thème.

• Premier point important
• Deuxième point à retenir
• Troisième élément

Ceci est un paragraphe plus long pour montrer comment le thème gère le contenu étendu et les séparateurs."""
        
        return self.apply_theme(
            content=sample_content,
            theme_name=theme_name,
            title="Aperçu du Thème",
            variables={"bot_name": "Link Center Bot", "channel_name": "Canal Test"}
        )
    
    def list_themes(self) -> List[Dict[str, str]]:
        """List available themes with descriptions"""
        themes_list = []
        for name, theme in self.themes.items():
            themes_list.append({
                "name": name,
                "display_name": theme.name,
                "primary_emoji": theme.primary_emoji,
                "description": f"Thème {theme.name} avec {theme.primary_emoji} {theme.secondary_emoji}"
            })
        return themes_list
    
    def set_channel_signature(self, channel_id: str, signature: str):
        """Set custom signature for a channel"""
        self.signatures[channel_id] = signature
        self._save_signatures(self.signatures)
    
    def get_channel_signature(self, channel_id: str, theme_name: str = "default") -> str:
        """Get signature for a channel"""
        return self.signatures.get(channel_id, self.signatures.get(theme_name, self.signatures["default"]))
    
    def format_welcome_message(self, username: str, theme_name: str = "community") -> str:
        """Format welcome message with theme"""
        content = f"""Bienvenue {username} ! 

Nous sommes ravis de vous accueillir dans notre communauté.

• Découvrez nos contenus quotidiens
• Participez aux sondages et discussions  
• Restez connecté pour ne rien manquer

N'hésitez pas à interagir et à partager vos idées !"""
        
        return self.apply_theme(
            content=content,
            theme_name=theme_name,
            title="Bienvenue !",
            variables={"username": username}
        )
    
    def format_daily_message(self, content: str, category: str, theme_name: Optional[str] = None) -> str:
        """Format daily message with appropriate theme"""
        if not theme_name:
            # Auto-select theme based on category
            theme_mapping = {
                "motivation": "motivational",
                "news": "professional", 
                "tips": "professional",
                "entertainment": "gaming",
                "community": "community"
            }
            theme_name = theme_mapping.get(category, "default")
        
        category_titles = {
            "motivation": "Motivation du Jour",
            "news": "Actualités",
            "tips": "Conseil du Jour", 
            "entertainment": "Divertissement",
            "community": "Communauté"
        }
        
        title = category_titles.get(category, "Message du Jour")
        
        return self.apply_theme(
            content=content,
            theme_name=theme_name,
            title=title
        )

# Global theme manager instance
theme_manager = ThemeManager()