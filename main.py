#!/usr/bin/env python3
"""
Main entry point for the Telegram Channel Management Bot
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.config import Config
from bot.handlers import setup_handlers
from bot.scheduler import SchedulerManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    try:
        # Initialize configuration
        config = Config()
        
        # Get bot token from environment
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN not found in environment variables")
            return
        
        # Initialize bot and dispatcher
        bot = Bot(token=bot_token)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Setup handlers
        setup_handlers(dp, config)
        
        # Initialize scheduler
        scheduler_manager = SchedulerManager(bot, config)
        await scheduler_manager.start()
        
        logger.info("Bot started successfully")
        
        # Start polling
        try:
            await dp.start_polling(bot)
        finally:
            await scheduler_manager.stop()
            await bot.session.close()
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
