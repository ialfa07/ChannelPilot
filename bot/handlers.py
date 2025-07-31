"""
Bot handlers for commands and events
"""

import logging
from datetime import datetime
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
        if not message.from_user:
            return
            
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name or "Utilisateur"
        
        # Log user info for admin setup
        logger.info(f"User {username} (ID: {user_id}) sent /start command")
        
        welcome_text = (
            f"🤖 **Bot de Gestion de Canal Telegram**\n\n"
            f"Bonjour {username} !\n"
            f"Votre ID utilisateur : `{user_id}`\n\n"
            "Commandes disponibles :\n"
            "• `/help` - Afficher l'aide\n"
            "• `/register_admin mot_de_passe` - Devenir administrateur\n"
            "• `/cid` - Obtenir l'ID du canal (dans le canal)\n"
            "• `/add_channel ID nom` - Ajouter un canal (admin)\n"
            "• `/status` - Statut des canaux (admin)\n"
            "• `/channels` - Liste des canaux gérés (admin)\n"
            "• `/customize_poll` - Personnaliser le sondage du jour (admin)\n"
            "• `/test_welcome` - Tester le message de bienvenue (admin)\n\n"
            "Fonctionnalités :\n"
            "✅ Messages de bienvenue automatiques\n"
            "✅ Messages quotidiens programmés\n"
            "✅ Sondages quotidiens (500+ abonnés)\n"
            "✅ Gestion multi-canaux"
        )
        await message.answer(welcome_text, parse_mode="Markdown")
    
    @router.message(Command("register_admin"))
    async def cmd_register_admin(message: Message):
        """Handle /register_admin command"""
        if not message.from_user or not message.text:
            return
        
        # Extract password from command
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ Usage: `/register_admin votre_mot_de_passe`")
            return
        
        password = args[1]
        # Simple password - you can change this
        correct_password = "admin2025"
        
        if password != correct_password:
            await message.answer("❌ Mot de passe incorrect.")
            logger.warning(f"Failed admin registration attempt by user {message.from_user.id}")
            return
        
        # Add user as admin
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name or "Admin"
        
        config.add_admin_user(user_id)
        
        await message.answer(
            f"✅ **Félicitations !**\n\n"
            f"Vous êtes maintenant administrateur du bot.\n"
            f"Toutes les commandes admin sont disponibles :\n\n"
            f"• `/status` - Voir le statut des canaux\n"
            f"• `/channels` - Gérer les canaux\n"
            f"• `/customize_poll` - Personnaliser les sondages\n"
            f"• `/test_welcome` - Tester les messages de bienvenue",
            parse_mode="Markdown"
        )
        
        logger.info(f"User {username} (ID: {user_id}) successfully registered as admin")
    
    @router.message(Command("add_channel"))
    async def cmd_add_channel(message: Message):
        """Handle /add_channel command"""
        if not message.from_user or not await is_admin(message.from_user.id, config):
            await message.answer("❌ Commande réservée aux administrateurs.")
            return
        
        if not message.text:
            await message.answer("❌ Erreur de commande.")
            return
            
        # Extract channel ID and name from command
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.answer(
                "❌ Usage: `/add_channel -1001234567890 Nom du Canal`\n\n"
                "Exemple: `/add_channel -1001234567890 Mon Super Canal`",
                parse_mode="Markdown"
            )
            return
        
        channel_id = args[1]
        channel_name = args[2]
        
        # Validate channel ID format
        if not channel_id.startswith('-'):
            await message.answer("❌ L'ID du canal doit commencer par '-' (exemple: -1001234567890)")
            return
        
        try:
            # Test if bot can access the channel
            if message.bot:
                chat = await message.bot.get_chat(channel_id)
                member_count = await get_channel_subscriber_count(message.bot, channel_id)
                
                # Add channel to configuration
                channel_info = {
                    "name": channel_name,
                    "active": True,
                    "description": f"Canal ajouté le {datetime.now().strftime('%Y-%m-%d')}",
                    "added_date": datetime.now().strftime('%Y-%m-%d')
                }
                
                config.add_channel(channel_id, channel_info)
                
                await message.answer(
                    f"✅ **Canal ajouté avec succès !**\n\n"
                    f"**Nom :** {chat.title}\n"
                    f"**ID :** {channel_id}\n"
                    f"**Abonnés :** {member_count}\n"
                    f"**Status :** Actif\n\n"
                    f"Le bot va maintenant gérer automatiquement :\n"
                    f"• Messages de bienvenue\n"
                    f"• Messages quotidiens à 9h00\n"
                    f"• Sondages quotidiens à 10h00 (si ≥500 abonnés)",
                    parse_mode="Markdown"
                )
                
                logger.info(f"Channel {channel_name} ({channel_id}) added by admin {message.from_user.id}")
                
        except Exception as e:
            logger.error(f"Error adding channel {channel_id}: {e}")
            await message.answer(
                f"❌ **Erreur lors de l'ajout du canal**\n\n"
                f"Vérifiez que :\n"
                f"• L'ID du canal est correct\n"
                f"• Le bot est administrateur du canal\n"
                f"• Le bot a les permissions nécessaires\n\n"
                f"Erreur: {str(e)[:100]}",
                parse_mode="Markdown"
            )
    
    @router.message(Command("cid"))
    async def cmd_get_channel_id(message: Message):
        """Handle /cid command - get channel ID"""
        try:
            if message.chat.type in ["channel", "supergroup"]:
                channel_id = str(message.chat.id)
                channel_name = message.chat.title or "Canal"
                member_count = 0
                
                try:
                    if message.bot:
                        member_count = await get_channel_subscriber_count(message.bot, channel_id)
                except:
                    pass
                
                await message.reply(
                    f"📋 **Informations du Canal**\n\n"
                    f"**Nom :** {channel_name}\n"
                    f"**ID :** `{channel_id}`\n"
                    f"**Abonnés :** {member_count}\n"
                    f"**Type :** {message.chat.type.title()}\n\n"
                    f"Pour ajouter ce canal :\n"
                    f"`/add_channel {channel_id} {channel_name}`",
                    parse_mode="Markdown"
                )
                
                logger.info(f"Channel ID requested: {channel_name} ({channel_id})")
                
            else:
                await message.answer(
                    "❌ Cette commande ne fonctionne que dans les canaux.\n"
                    "Envoyez `/cid` directement dans votre canal."
                )
                
        except Exception as e:
            logger.error(f"Error getting channel ID: {e}")
            await message.answer("❌ Erreur lors de la récupération de l'ID du canal.")
    
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
                    status_text += f"• ID: {channel_id}\n"
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
                    channels_text += f"• ID: {channel_id}\n"
                    username_text = f"@{chat.username}" if chat.username else "N/A"
                    channels_text += f"• Username: {username_text}\n"
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
    
    # Handle messages in channels (for detecting channel IDs)
    @router.message(F.chat.type.in_({"channel", "supergroup"}))
    async def handle_channel_message(message: Message):
        """Handle messages in channels to detect channel IDs"""
        try:
            if message.text and "@Link_CenterBot" in message.text:
                channel_id = str(message.chat.id)
                channel_name = message.chat.title or "Canal"
                
                logger.info(f"Bot mentioned in channel: {channel_name} (ID: {channel_id})")
                
                # Send info message to channel
                await message.reply(
                    f"🤖 **Canal Détecté !**\n\n"
                    f"**Nom :** {channel_name}\n"
                    f"**ID :** {channel_id}\n\n"
                    f"Pour ajouter ce canal à la gestion automatique, "
                    f"contactez l'administrateur avec ces informations.",
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Error handling channel message: {e}")

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
