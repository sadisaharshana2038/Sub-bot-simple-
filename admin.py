"""
🎬 ADMIN MODULE
Admin functions for content management
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Conversation states
AWAITING_SERIES_INFO, AWAITING_EPISODE_INFO = range(2)

# ============================================
# ADMIN FUNCTIONS
# ============================================

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users"""
    from bot import db, ADMIN_IDS, E
    
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} No permission!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /broadcast Your message here\n\n"
            "This will send to all users!"
        )
        return
    
    message = ' '.join(context.args)
    
    # Get all users
    users = await db.db.users.find({}).to_list(None)
    
    sent = 0
    failed = 0
    
    await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    
    for user_data in users:
        try:
            await context.bot.send_message(
                chat_id=user_data['user_id'],
                text=f"📢 *Broadcast*\n\n{message}",
                parse_mode='Markdown'
            )
            sent += 1
        except:
            failed += 1
    
    await update.message.reply_text(
        f"✅ Broadcast complete!\n\n"
        f"Sent: {sent}\n"
        f"Failed: {failed}"
    )

async def add_series_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding series"""
    from bot import ADMIN_IDS, E
    
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} No permission!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📝 *Add New Series*\n\n"
        "Send series information in this format:\n\n"
        "```\n"
        "series_id: breaking_bad\n"
        "title_en: Breaking Bad\n"
        "title_si: බ්‍රේකින් බෑඩ්\n"
        "description_en: A chemistry teacher...\n"
        "description_si: රසායන ගුරුවරයෙක්...\n"
        "category: Drama\n"
        "rating: 9.5\n"
        "poster_url: https://example.com/poster.jpg\n"
        "```\n\n"
        "Or /cancel to cancel",
        parse_mode='Markdown'
    )
    
    return AWAITING_SERIES_INFO

async def receive_series_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save series info"""
    from bot import db, E
    
    text = update.message.text
    lines = text.strip().split('\n')
    
    series_data = {
        'is_active': True,
        'is_featured': False,
        'is_trending': False,
        'is_new': True,
        'episodes': 0,
        'views': 0,
        'downloads': 0,
        'added_date': datetime.now(),
        'added_by': update.effective_user.id
    }
    
    # Parse data
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key == 'rating':
                value = float(value)
            
            series_data[key] = value
    
    # Validate required fields
    if 'series_id' not in series_data:
        await update.message.reply_text(f"{E['error']} series_id is required!")
        return AWAITING_SERIES_INFO
    
    # Save to database
    try:
        await db.db.series.insert_one(series_data)
        await update.message.reply_text(
            f"{E['success']} Series added successfully!\n\n"
            f"ID: {series_data.get('series_id')}\n"
            f"Title: {series_data.get('title_en', 'N/A')}"
        )
    except Exception as e:
        await update.message.reply_text(f"{E['error']} Error: {e}")
    
    return ConversationHandler.END

async def add_episode_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding episode"""
    from bot import ADMIN_IDS, E
    
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} No permission!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📺 *Add New Episode*\n\n"
        "Send episode information:\n\n"
        "```\n"
        "episode_id: bb_s01e01\n"
        "series_id: breaking_bad\n"
        "season: 1\n"
        "episode: 1\n"
        "title: Pilot\n"
        "file_id: BAACAgIAAxkBAAI...\n"
        "```\n\n"
        "Or /cancel",
        parse_mode='Markdown'
    )
    
    return AWAITING_EPISODE_INFO

async def receive_episode_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save episode info"""
    from bot import db, E
    
    text = update.message.text
    lines = text.strip().split('\n')
    
    episode_data = {
        'is_active': True,
        'downloads': 0,
        'views': 0,
        'added_date': datetime.now(),
        'added_by': update.effective_user.id
    }
    
    # Parse data
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key in ['season', 'episode']:
                value = int(value)
            
            episode_data[key] = value
    
    # Validate
    if 'episode_id' not in episode_data or 'series_id' not in episode_data:
        await update.message.reply_text(f"{E['error']} episode_id and series_id required!")
        return AWAITING_EPISODE_INFO
    
    # Save
    try:
        await db.db.episodes.insert_one(episode_data)
        
        # Update series episode count
        await db.db.series.update_one(
            {'series_id': episode_data['series_id']},
            {'$inc': {'episodes': 1}}
        )
        
        await update.message.reply_text(
            f"{E['success']} Episode added!\n\n"
            f"ID: {episode_data.get('episode_id')}\n"
            f"Series: {episode_data.get('series_id')}"
        )
    except Exception as e:
        await update.message.reply_text(f"{E['error']} Error: {e}")
    
    return ConversationHandler.END

async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    await update.message.reply_text("❌ Operation cancelled")
    return ConversationHandler.END

async def view_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View bot statistics"""
    from bot import db, ADMIN_IDS, E
    
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} No permission!")
        return
    
    # Get stats
    total_users = await db.db.users.count_documents({})
    total_series = await db.db.series.count_documents({})
    total_episodes = await db.db.episodes.count_documents({})
    total_downloads = await db.db.downloads.count_documents({})
    
    # Get active users (last 7 days)
    from datetime import timedelta
    week_ago = datetime.now() - timedelta(days=7)
    active_users = await db.db.users.count_documents({'last_active': {'$gte': week_ago}})
    
    stats_text = f"""
📊 *Bot Statistics*

━━━━━━━━━━━━━━━━━━━━

👥 *Users:*
Total: {total_users:,}
Active (7d): {active_users:,}

━━━━━━━━━━━━━━━━━━━━

📺 *Content:*
Series: {total_series:,}
Episodes: {total_episodes:,}

━━━━━━━━━━━━━━━━━━━━

📥 *Activity:*
Downloads: {total_downloads:,}

━━━━━━━━━━━━━━━━━━━━
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# ============================================
# CONVERSATION HANDLER
# ============================================

def get_admin_handlers():
    """Get admin conversation handlers"""
    
    add_series_conv = ConversationHandler(
        entry_points=[CommandHandler('addseries', add_series_start)],
        states={
            AWAITING_SERIES_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_series_info)]
        },
        fallbacks=[CommandHandler('cancel', cancel_operation)]
    )
    
    add_episode_conv = ConversationHandler(
        entry_points=[CommandHandler('addepisode', add_episode_start)],
        states={
            AWAITING_EPISODE_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_episode_info)]
        },
        fallbacks=[CommandHandler('cancel', cancel_operation)]
    )
    
    return [
        add_series_conv,
        add_episode_conv,
        CommandHandler('broadcast', broadcast_command),
        CommandHandler('viewstats', view_stats)
    ]
