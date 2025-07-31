"""
Bot handlers for commands and events
"""

import logging
from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED, LEFT, RESTRICTED, MEMBER, ADMINISTRATOR, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from .config import Config
from .utils import is_admin, format_welcome_message, get_channel_subscriber_count

logger = logging.getLogger(__name__)

# FSM States for poll customization
class PollCustomization(StatesGroup):
    waiting_for_options = State()
    waiting_for_confirmation = State()

def setup_handlers(dp, config: Config):
    """Setup all bot handlers"""
    router = Router()
    
    @router.message(Command("start"))
    async def cmd_start(message: Message):
        """Handle /start command"""
        welcome_text = (
            "🤖 **Bot de Gestion de Canal Telegram**\n\n"
            "Commandes disponibles :\n"
            "• `/help` - Afficher l'aide\n"
            "• `/status` - Statut des canaux\n"
            "• `/customize_poll` - Personnaliser le sondage du jour\n"
            "• `/test_welcome` - Tester le message de bienvenue\n"
            "• `/channels` - Liste des canaux gérés\n\n"
            "Fonctionnalités :\n"
            "✅ Messages de bienvenue automatiques\n"
            "✅ Messages quotidiens programmés\n"
            "✅ Sondages quotidiens (500+ abonnés)\n"
            "✅ Gestion multi-canaux"
        )
        await message.answer(welcome_text, parse_mode="Markdown")
    
    @router.message(Command("help"))
    async def cmd_help(message: Message):
        """Handle /help command"""
        help_text = (
            "📖 **Guide d'utilisation**\n\n"
            "**Commandes Admin :**\n"
            "• `/status` - Voir le statut de tous les canaux\n"
            "• `/customize_poll` - Personnaliser les options du sondage quotidien\n"
            "• `/test_welcome @username` - Tester le message de bienvenue\n"
            "• `/channels` - Liste des canaux avec leurs statistiques\n\n"
            "**Fonctionnement automatique :**\n"
            "• Messages de bienvenue envoyés automatiquement\n"
            "• Messages quotidiens selon la configuration\n"
            "• Sondages quotidiens (si canal ≥ 500 abonnés)\n\n"
            "**Configuration :**\n"
            "• Modifiez `config/messages.json` pour les textes\n"
            "• Modifiez `config/channels.json` pour les canaux\n"
            "• Utilisez `.env` pour le token du bot"
        )
        await message.answer(help_text, parse_mode="Markdown")
    
    @router.message(Command("status"))
    async def cmd_status(message: Message):
        """Handle /status command - show channel status"""
        if not message.from_user or not await is_admin(message.from_user.id, config):
            await message.answer("❌ Commande réservée aux administrateurs.")
            return
        
        try:
            channels = config.get_channels()
            if not channels:
                await message.answer("❌ Aucun canal configuré.")
                return
            
            status_text = "📊 **Statut des Canaux**\n\n"
            
            for channel_id, channel_info in channels.items():
                try:
                    # Get channel info
                    if not message.bot:
                        continue
                    chat = await message.bot.get_chat(channel_id)
                    member_count = await get_channel_subscriber_count(message.bot, channel_id)
                    
                    status_text += f"📢 **{chat.title}**\n"
                    status_text += f"• ID: `{channel_id}`\n"
                    status_text += f"• Abonnés: {member_count}\n"
                    status_text += f"• Sondages: {'✅' if member_count >= 500 else '❌ (< 500)'}\n"
                    status_text += f"• Actif: {'✅' if channel_info.get('active', True) else '❌'}\n\n"
                    
                except Exception as e:
                    status_text += f"❌ **Canal {channel_id}**\n"
                    status_text += f"• Erreur: {str(e)}\n\n"
            
            await message.answer(status_text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await message.answer(f"❌ Erreur lors de la récupération du statut: {e}")
    
    @router.message(Command("channels"))
    async def cmd_channels(message: Message):
        """Handle /channels command - list managed channels"""
        if not message.from_user or not await is_admin(message.from_user.id, config):
            await message.answer("❌ Commande réservée aux administrateurs.")
            return
        
        try:
            channels = config.get_channels()
            if not channels:
                await message.answer("❌ Aucun canal configuré.")
                return
            
            channels_text = "📋 **Canaux Gérés**\n\n"
            
            for channel_id, channel_info in channels.items():
                try:
                    if not message.bot:
                        continue
                    chat = await message.bot.get_chat(channel_id)
                    member_count = await get_channel_subscriber_count(message.bot, channel_id)
                    
                    channels_text += f"📢 **{chat.title}**\n"
                    channels_text += f"• ID: `{channel_id}`\n"
                    channels_text += f"• Username: @{chat.username if chat.username else 'N/A'}\n"
                    channels_text += f"• Abonnés: {member_count}\n"
                    channels_text += f"• Description: {chat.description[:50] + '...' if chat.description else 'N/A'}\n\n"
                    
                except Exception as e:
                    channels_text += f"❌ **Canal {channel_id}**: Erreur d'accès\n\n"
            
            await message.answer(channels_text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in channels command: {e}")
            await message.answer(f"❌ Erreur: {e}")
    
    @router.message(Command("customize_poll"))
    async def cmd_customize_poll(message: Message, state: FSMContext):
        """Handle /customize_poll command"""
        if not message.from_user or not await is_admin(message.from_user.id, config):
            await message.answer("❌ Commande réservée aux administrateurs.")
            return
        
        current_options = config.get_poll_options()
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(current_options)])
        
        await message.answer(
            f"🗳️ **Personnalisation du Sondage Quotidien**\n\n"
            f"**Options actuelles :**\n{options_text}\n\n"
            f"Envoyez les nouvelles options séparées par des virgules.\n"
            f"Exemple: `Motivé 💪, Fatigué 😴, Neutre 😐`\n\n"
            f"Ou tapez /cancel pour annuler.",
            parse_mode="Markdown"
        )
        await state.set_state(PollCustomization.waiting_for_options)
    
    @router.message(PollCustomization.waiting_for_options)
    async def process_poll_options(message: Message, state: FSMContext):
        """Process new poll options"""
        if message.text and message.text.startswith('/cancel'):
            await state.clear()
            await message.answer("❌ Personnalisation annulée.")
            return
        
        try:
            # Parse options
            if not message.text:
                await message.answer("❌ Veuillez envoyer du texte.")
                return
            options = [opt.strip() for opt in message.text.split(',') if opt.strip()]
            
            if len(options) < 2:
                await message.answer("❌ Veuillez fournir au moins 2 options.")
                return
            
            if len(options) > 10:
                await message.answer("❌ Maximum 10 options autorisées.")
                return
            
            # Store options in state
            await state.update_data(new_options=options)
            
            # Show confirmation
            options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Confirmer", callback_data="confirm_poll"),
                    InlineKeyboardButton(text="❌ Annuler", callback_data="cancel_poll")
                ]
            ])
            
            await message.answer(
                f"🗳️ **Nouvelles options du sondage :**\n\n{options_text}\n\n"
                f"Confirmer ces options ?",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            await state.set_state(PollCustomization.waiting_for_confirmation)
            
        except Exception as e:
            logger.error(f"Error processing poll options: {e}")
            await message.answer(f"❌ Erreur lors du traitement: {e}")
            await state.clear()
    
    @router.callback_query(F.data == "confirm_poll")
    async def confirm_poll_options(callback, state: FSMContext):
        """Confirm new poll options"""
        try:
            data = await state.get_data()
            new_options = data.get('new_options', [])
            
            # Update configuration
            config.update_poll_options(new_options)
            
            options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(new_options)])
            
            await callback.message.edit_text(
                f"✅ **Sondage mis à jour !**\n\n"
                f"**Nouvelles options :**\n{options_text}\n\n"
                f"Ces options seront utilisées pour le prochain sondage quotidien.",
                parse_mode="Markdown"
            )
            
            await state.clear()
            
        except Exception as e:
            logger.error(f"Error confirming poll options: {e}")
            await callback.message.edit_text(f"❌ Erreur lors de la confirmation: {e}")
            await state.clear()
    
    @router.callback_query(F.data == "cancel_poll")
    async def cancel_poll_options(callback, state: FSMContext):
        """Cancel poll customization"""
        await callback.message.edit_text("❌ Personnalisation du sondage annulée.")
        await state.clear()
    
    @router.message(Command("test_welcome"))
    async def cmd_test_welcome(message: Message):
        """Handle /test_welcome command"""
        if not message.from_user or not await is_admin(message.from_user.id, config):
            await message.answer("❌ Commande réservée aux administrateurs.")
            return
        
        # Extract username from command
        if not message.text:
            await message.answer("❌ Erreur de commande.")
            return
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            test_user = args[1].replace('@', '')
        else:
            test_user = message.from_user.first_name or message.from_user.username or "TestUser"
        
        welcome_msg = format_welcome_message(config.get_welcome_message(), test_user)
        
        await message.answer(
            f"🧪 **Test du message de bienvenue :**\n\n{welcome_msg}",
            parse_mode="Markdown"
        )
    
    # Channel member updates handler
    @router.chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED >> MEMBER))
    @router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT >> MEMBER))
    @router.chat_member(ChatMemberUpdatedFilter(member_status_changed=RESTRICTED >> MEMBER))
    async def on_user_join_channel(chat_member: ChatMemberUpdated):
        """Handle user joining channel"""
        try:
            # Check if this channel is managed by the bot
            channels = config.get_channels()
            channel_id = str(chat_member.chat.id)
            
            if channel_id not in channels:
                return
            
            # Get user info
            user = chat_member.new_chat_member.user
            username = user.username or user.first_name or "Nouvel abonné"
            
            # Format and send welcome message
            welcome_msg = format_welcome_message(config.get_welcome_message(), username)
            
            try:
                # Try to send private message first
                if chat_member.bot:
                    await chat_member.bot.send_message(user.id, welcome_msg, parse_mode="Markdown")
                    logger.info(f"Welcome message sent privately to {username}")
            except:
                # If private message fails, send to channel
                try:
                    if chat_member.bot:
                        await chat_member.bot.send_message(chat_member.chat.id, welcome_msg, parse_mode="Markdown")
                        logger.info(f"Welcome message sent to channel for {username}")
                except Exception as e:
                    logger.error(f"Failed to send welcome message: {e}")
            
        except Exception as e:
            logger.error(f"Error handling user join: {e}")
    
    dp.include_router(router)
