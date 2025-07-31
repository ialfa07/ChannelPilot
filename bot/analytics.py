"""
Analytics and Statistics Module for Telegram Bot
Tracks channel growth, engagement, and provides reporting
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ChannelStats:
    """Channel statistics data structure"""
    channel_id: str
    timestamp: str
    subscriber_count: int
    messages_sent: int
    polls_sent: int
    engagement_rate: float = 0.0
    
@dataclass
class MessageStats:
    """Message statistics data structure"""
    message_id: int
    channel_id: str
    timestamp: str
    message_type: str  # 'daily', 'poll', 'welcome', 'custom'
    views: int = 0
    reactions: int = 0
    forwards: int = 0
    engagement_score: float = 0.0

class AnalyticsManager:
    """Manages analytics data collection and reporting"""
    
    def __init__(self, data_file: str = "analytics_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load analytics data from file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "channel_stats": [],
                "message_stats": [],
                "daily_summaries": [],
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
            return {"channel_stats": [], "message_stats": [], "daily_summaries": []}
    
    def _save_data(self):
        """Save analytics data to file"""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
    
    def record_channel_stats(self, channel_id: str, subscriber_count: int, 
                           messages_sent: int = 0, polls_sent: int = 0):
        """Record channel statistics"""
        stats = ChannelStats(
            channel_id=channel_id,
            timestamp=datetime.now().isoformat(),
            subscriber_count=subscriber_count,
            messages_sent=messages_sent,
            polls_sent=polls_sent
        )
        
        self.data["channel_stats"].append(asdict(stats))
        self._save_data()
        logger.info(f"Recorded stats for channel {channel_id}: {subscriber_count} subscribers")
    
    def record_message_stats(self, message_id: int, channel_id: str, 
                           message_type: str, views: int = 0, reactions: int = 0):
        """Record message statistics"""
        stats = MessageStats(
            message_id=message_id,
            channel_id=channel_id,
            timestamp=datetime.now().isoformat(),
            message_type=message_type,
            views=views,
            reactions=reactions
        )
        
        self.data["message_stats"].append(asdict(stats))
        self._save_data()
        logger.info(f"Recorded message stats: {message_type} in {channel_id}")
    
    def get_channel_growth(self, channel_id: str, days: int = 30) -> List[Dict]:
        """Get channel growth data for specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        growth_data = []
        for stat in self.data["channel_stats"]:
            if (stat["channel_id"] == channel_id and 
                datetime.fromisoformat(stat["timestamp"]) >= cutoff_date):
                growth_data.append(stat)
        
        return sorted(growth_data, key=lambda x: x["timestamp"])
    
    def get_engagement_stats(self, channel_id: str, days: int = 7) -> Dict[str, Any]:
        """Calculate engagement statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        messages = [
            msg for msg in self.data["message_stats"]
            if (msg["channel_id"] == channel_id and 
                datetime.fromisoformat(msg["timestamp"]) >= cutoff_date)
        ]
        
        if not messages:
            return {"total_messages": 0, "avg_views": 0, "avg_reactions": 0, "engagement_rate": 0}
        
        total_views = sum(msg["views"] for msg in messages)
        total_reactions = sum(msg["reactions"] for msg in messages)
        total_messages = len(messages)
        
        return {
            "total_messages": total_messages,
            "avg_views": total_views / total_messages if total_messages > 0 else 0,
            "avg_reactions": total_reactions / total_messages if total_messages > 0 else 0,
            "engagement_rate": (total_reactions / total_views * 100) if total_views > 0 else 0,
            "period_days": days
        }
    
    def generate_weekly_report(self, channel_id: str) -> str:
        """Generate weekly analytics report"""
        growth_data = self.get_channel_growth(channel_id, 7)
        engagement = self.get_engagement_stats(channel_id, 7)
        
        if not growth_data:
            return f"📊 **Rapport Hebdomadaire - Canal {channel_id}**\n\nAucune donnée disponible pour cette période."
        
        # Calculate growth
        start_subs = growth_data[0]["subscriber_count"] if growth_data else 0
        end_subs = growth_data[-1]["subscriber_count"] if growth_data else 0
        growth = end_subs - start_subs
        growth_percent = (growth / start_subs * 100) if start_subs > 0 else 0
        
        report = f"""📊 **Rapport Hebdomadaire**

**Croissance des Abonnés:**
• Début: {start_subs:,} abonnés
• Fin: {end_subs:,} abonnés
• Croissance: {growth:+,} ({growth_percent:+.1f}%)

**Engagement:**
• Messages envoyés: {engagement['total_messages']}
• Vues moyennes: {engagement['avg_views']:.0f}
• Réactions moyennes: {engagement['avg_reactions']:.0f}
• Taux d'engagement: {engagement['engagement_rate']:.1f}%

**Période:** 7 derniers jours
**Généré le:** {datetime.now().strftime('%d/%m/%Y à %H:%M')}"""
        
        return report
    
    def generate_monthly_report(self, channel_id: str) -> str:
        """Generate monthly analytics report"""
        growth_data = self.get_channel_growth(channel_id, 30)
        engagement = self.get_engagement_stats(channel_id, 30)
        
        if not growth_data:
            return f"📊 **Rapport Mensuel - Canal {channel_id}**\n\nAucune donnée disponible pour cette période."
        
        # Calculate growth
        start_subs = growth_data[0]["subscriber_count"] if growth_data else 0
        end_subs = growth_data[-1]["subscriber_count"] if growth_data else 0
        growth = end_subs - start_subs
        growth_percent = (growth / start_subs * 100) if start_subs > 0 else 0
        
        # Weekly breakdown
        weekly_data = []
        for i in range(4):
            week_start = datetime.now() - timedelta(days=30-i*7)
            week_end = week_start + timedelta(days=7)
            week_growth = self.get_channel_growth(channel_id, 7)
            if week_growth:
                weekly_data.append(len(week_growth))
        
        report = f"""📊 **Rapport Mensuel Détaillé**

**Croissance des Abonnés (30 jours):**
• Début: {start_subs:,} abonnés
• Fin: {end_subs:,} abonnés
• Croissance totale: {growth:+,} ({growth_percent:+.1f}%)
• Croissance moyenne/jour: {growth/30:.1f}

**Engagement (30 jours):**
• Messages envoyés: {engagement['total_messages']}
• Vues moyennes: {engagement['avg_views']:.0f}
• Réactions moyennes: {engagement['avg_reactions']:.0f}
• Taux d'engagement: {engagement['engagement_rate']:.1f}%

**Performance:**
• Meilleur jour: À venir
• Messages les plus populaires: À venir

**Période:** 30 derniers jours
**Généré le:** {datetime.now().strftime('%d/%m/%Y à %H:%M')}"""
        
        return report
    
    async def update_channel_stats(self, bot, channel_id: str):
        """Update channel statistics from Telegram API"""
        try:
            # Get current subscriber count
            chat = await bot.get_chat(channel_id)
            member_count = await bot.get_chat_member_count(channel_id)
            
            # Record the stats
            self.record_channel_stats(channel_id, member_count)
            
            return member_count
        except Exception as e:
            logger.error(f"Error updating stats for channel {channel_id}: {e}")
            return 0
    
    def get_dashboard_data(self, channel_id: str) -> Dict[str, Any]:
        """Get dashboard data for a channel"""
        recent_growth = self.get_channel_growth(channel_id, 7)
        engagement = self.get_engagement_stats(channel_id, 7)
        
        current_subs = recent_growth[-1]["subscriber_count"] if recent_growth else 0
        growth_7d = (recent_growth[-1]["subscriber_count"] - recent_growth[0]["subscriber_count"]) if len(recent_growth) >= 2 else 0
        
        return {
            "current_subscribers": current_subs,
            "growth_7d": growth_7d,
            "engagement_rate": engagement["engagement_rate"],
            "total_messages": engagement["total_messages"],
            "avg_views": engagement["avg_views"]
        }

# Global analytics manager instance
analytics = AnalyticsManager()