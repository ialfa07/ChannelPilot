"""
Scheduler for automated tasks (daily messages and polls)
"""

import logging
import asyncio
from datetime import datetime, time
from typing import Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from aiogram.types import Poll

from .config import Config
from .utils import get_channel_subscriber_count

logger = logging.getLogger(__name__)

class SchedulerManager:
    """Manages scheduled tasks for the bot"""
    
    def __init__(self, bot: Bot, config: Config):
        self.bot = bot
        self.config = config
        self.scheduler = AsyncIOScheduler()
        
    async def start(self):
        """Start the scheduler"""
        try:
            # Schedule daily messages
            daily_config = self.config.get_daily_message_config()
            if daily_config.get('enabled', True):
                hour = daily_config.get('hour', 9)
                minute = daily_config.get('minute', 0)
                
                self.scheduler.add_job(
                    self._send_daily_messages,
                    CronTrigger(hour=hour, minute=minute),
                    id='daily_messages',
                    name='Send Daily Messages'
                )
                logger.info(f"Scheduled daily messages at {hour:02d}:{minute:02d}")
            
            # Schedule daily polls
            poll_config = self.config.get_poll_config()
            if poll_config.get('enabled', True):
                hour = poll_config.get('hour', 10)
                minute = poll_config.get('minute', 0)
                
                self.scheduler.add_job(
                    self._send_daily_polls,
                    CronTrigger(hour=hour, minute=minute),
                    id='daily_polls',
                    name='Send Daily Polls'
                )
                logger.info(f"Scheduled daily polls at {hour:02d}:{minute:02d}")
            
            self.scheduler.start()
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def _send_daily_messages(self):
        """Send daily messages to all configured channels"""
        try:
            channels = self.config.get_channels()
            daily_messages = self.config.get_daily_messages()
            
            if not daily_messages:
                logger.warning("No daily messages configured")
                return
            
            # Get today's message (cycle through messages)
            today = datetime.now()
            message_index = today.timetuple().tm_yday % len(daily_messages)
            message = daily_messages[message_index]
            
            logger.info(f"Sending daily message to {len(channels)} channels")
            
            for channel_id, channel_info in channels.items():
                if not channel_info.get('active', True):
                    continue
                
                try:
                    await self.bot.send_message(
                        chat_id=channel_id,
                        text=message,
                        parse_mode="Markdown"
                    )
                    logger.info(f"Daily message sent to channel {channel_id}")
                    
                    # Small delay to avoid rate limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to send daily message to {channel_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in daily message task: {e}")
    
    async def _send_daily_polls(self):
        """Send daily polls to channels with 500+ subscribers"""
        try:
            channels = self.config.get_channels()
            poll_config = self.config.get_poll_config()
            poll_options = self.config.get_poll_options()
            
            if not poll_options:
                logger.warning("No poll options configured")
                return
            
            poll_question = poll_config.get('question', 'Comment vous sentez-vous aujourd\'hui ?')
            logger.info(f"Sending daily polls to eligible channels")
            
            for channel_id, channel_info in channels.items():
                if not channel_info.get('active', True):
                    continue
                
                try:
                    # Check subscriber count
                    subscriber_count = await get_channel_subscriber_count(self.bot, channel_id)
                    
                    if subscriber_count < 500:
                        logger.info(f"Channel {channel_id} has {subscriber_count} subscribers (< 500), skipping poll")
                        continue
                    
                    # Send poll
                    from aiogram.types import InputPollOption
                    poll_options_formatted = [InputPollOption(text=option) for option in poll_options]
                    
                    await self.bot.send_poll(
                        chat_id=channel_id,
                        question=poll_question,
                        options=poll_options_formatted,
                        is_anonymous=True,
                        allows_multiple_answers=False
                    )
                    
                    logger.info(f"Daily poll sent to channel {channel_id} ({subscriber_count} subscribers)")
                    
                    # Small delay to avoid rate limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to send poll to {channel_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in daily poll task: {e}")
    
    def reschedule_daily_messages(self, hour: int, minute: int):
        """Reschedule daily messages"""
        try:
            if self.scheduler.get_job('daily_messages'):
                self.scheduler.remove_job('daily_messages')
            
            self.scheduler.add_job(
                self._send_daily_messages,
                CronTrigger(hour=hour, minute=minute),
                id='daily_messages',
                name='Send Daily Messages'
            )
            logger.info(f"Rescheduled daily messages to {hour:02d}:{minute:02d}")
            
        except Exception as e:
            logger.error(f"Error rescheduling daily messages: {e}")
    
    def reschedule_daily_polls(self, hour: int, minute: int):
        """Reschedule daily polls"""
        try:
            if self.scheduler.get_job('daily_polls'):
                self.scheduler.remove_job('daily_polls')
            
            self.scheduler.add_job(
                self._send_daily_polls,
                CronTrigger(hour=hour, minute=minute),
                id='daily_polls',
                name='Send Daily Polls'
            )
            logger.info(f"Rescheduled daily polls to {hour:02d}:{minute:02d}")
            
        except Exception as e:
            logger.error(f"Error rescheduling daily polls: {e}")
