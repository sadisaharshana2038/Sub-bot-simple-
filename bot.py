"""
🎬 SINHALA SUBTITLE BOT - ULTRA PRO
සිංහල උපසිරැසි බොට් - සම්පූර්ණ ක්‍රියාකාරී bot එකක්

All-in-one bot with complete functionality
"""

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'sinhala_sub_bot')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
CHANNEL_ID = os.getenv('CHANNEL_ID', '')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@YourChannel')
FORCE_SUBSCRIBE = os.getenv('FORCE_SUBSCRIBE', 'true').lower() == 'true'

# Image URLs (Upload your images to Telegram first, then get the file_id or use Telegraph)
IMAGES = {
    'welcome': 'https://telegra.ph/file/welcome-banner.jpg',
    'loading': 'https://telegra.ph/file/loading.gif',
    'success': 'https://telegra.ph/file/success.jpg',
    'error': 'https://telegra.ph/file/error.jpg',
    'placeholder': 'https://telegra.ph/file/series-placeholder.jpg',
}

# Emojis
E = {
    'series': '🎬', 'episode': '📺', 'download': '⬇️', 'search': '🔍',
    'back': '🔙', 'home': '🏠', 'settings': '⚙️', 'help': 'ℹ️',
    'success': '✅', 'error': '❌', 'warning': '⚠️', 'loading': '🔄',
    'star': '⭐', 'fire': '🔥', 'new': '🆕', 'admin': '👑'
}

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# DATABASE CONNECTION
# ============================================

class Database:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(MONGODB_URI)
            await self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            await self._create_indexes()
            logger.info(f"✅ Connected to MongoDB: {DB_NAME}")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
    
    async def _create_indexes(self):
        """Create database indexes"""
        await self.db.users.create_index("user_id", unique=True)
        await self.db.series.create_index("series_id", unique=True)
        await self.db.episodes.create_index("episode_id", unique=True)
        await self.db.downloads.create_index("user_id")
    
    async def disconnect(self):
        if self.client:
            self.client.close()

# Global database instance
db = Database()

# ============================================
# HELPER FUNCTIONS
# ============================================

async def save_user(user):
    """Save or update user in database"""
    try:
        existing = await db.db.users.find_one({'user_id': user.id})
        
        if existing:
            await db.db.users.update_one(
                {'user_id': user.id},
                {
                    '$set': {
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'last_active': datetime.now()
                    },
                    '$inc': {'session_count': 1}
                }
            )
        else:
            new_user = {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'language_code': user.language_code,
                'joined_date': datetime.now(),
                'last_active': datetime.now(),
                'is_admin': user.id in ADMIN_IDS,
                'downloads': 0,
                'searches': 0,
                'points': 0,
                'language': 'si',
                'session_count': 1
            }
            await db.db.users.insert_one(new_user)
            logger.info(f"New user: {user.id} (@{user.username})")
    except Exception as e:
        logger.error(f"Error saving user: {e}")

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is subscribed to channel"""
    if not FORCE_SUBSCRIBE or not CHANNEL_ID:
        return True
    
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def get_user_data(user_id: int):
    """Get user data from database"""
    return await db.db.users.find_one({'user_id': user_id})

# ============================================
# MESSAGE TEMPLATES
# ============================================

def welcome_message(name: str, lang: str = 'si'):
    """Generate welcome message"""
    if lang == 'si':
        text = f"""
{E['series']} *සුභ පැතුම් {name}!* 🇱🇰

┏━━━━━━━━━━━━━━━━━━━━┓
┃  *SINHALA SUB BOT*  ┃
┗━━━━━━━━━━━━━━━━━━━━┛

{E['star']} *අපගේ විශේෂාංග:*

📚 විශාල එකතුවක් - 500+ කතා මාලා
{E['search']} පහසු සෙවීම - ක්ෂණික ප්‍රතිඵල
⚡ වේගවත් බාගත කිරීම - සෘජු ලින්ක්
💎 ප්‍රමිය අන්තර්ගතය - 4K උපසිරැසි

━━━━━━━━━━━━━━━━━━━━
{E['help']} *ආරම්භ කරන්න:*
පහත බොත්තම් ඔබන්න 👇
        """
    else:
        text = f"""
{E['series']} *Welcome {name}!* 🇱🇰

┏━━━━━━━━━━━━━━━━━━━━┓
┃  *SINHALA SUB BOT*  ┃
┗━━━━━━━━━━━━━━━━━━━━┛

{E['star']} *Our Features:*

📚 Huge Collection - 500+ Series
{E['search']} Easy Search - Instant Results
⚡ Fast Downloads - Direct Links
💎 Premium Content - 4K Subtitles

━━━━━━━━━━━━━━━━━━━━
{E['help']} *Get Started:*
Click buttons below 👇
        """
    
    keyboard = [
        [
            InlineKeyboardButton(f"{E['series']} Series | කතා මාලා", callback_data="browse"),
            InlineKeyboardButton(f"{E['search']} Search | සොයන්න", callback_data="search")
        ],
        [
            InlineKeyboardButton(f"{E['star']} Featured | විශේෂාංග", callback_data="featured"),
            InlineKeyboardButton(f"{E['fire']} Trending | ජනප්‍රිය", callback_data="trending")
        ],
        [
            InlineKeyboardButton("📝 Request | ඉල්ලීමක්", callback_data="request"),
            InlineKeyboardButton(f"{E['help']} Help | උදව්", callback_data="help")
        ],
        [
            InlineKeyboardButton("📊 Stats | සංඛ්‍යා", callback_data="stats"),
            InlineKeyboardButton(f"{E['settings']} Settings", callback_data="settings")
        ]
    ]
    
    if CHANNEL_USERNAME:
        keyboard.append([
            InlineKeyboardButton(f"📢 Join Channel | නාලිකාව", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        ])
    
    return text, InlineKeyboardMarkup(keyboard)

def series_card(series: dict, lang: str = 'si'):
    """Generate series card message"""
    if lang == 'si':
        text = f"""
{E['series']} *{series.get('title_si', 'Unknown')}*
📺 _{series.get('title_en', 'Unknown')}_

━━━━━━━━━━━━━━━━━━━━

📖 *විස්තරය:*
{series.get('description_si', 'විස්තරයක් නැත')[:200]}...

━━━━━━━━━━━━━━━━━━━━

📊 *තොරතුරු:*
🎭 ප්‍රභේදය: {series.get('category', 'N/A')}
📺 කථාංග: {series.get('episodes', 0)}
⭐ ශ්‍රේණිය: {series.get('rating', 0):.1f}/10
👁️ නැරඹුම්: {series.get('views', 0):,}

━━━━━━━━━━━━━━━━━━━━

🎯 *ලබා ගත හැකි:*
💾 720p, 1080p, 4K
🗣️ සිංහල උපසිරැසි

━━━━━━━━━━━━━━━━━━━━
        """
    else:
        text = f"""
{E['series']} *{series.get('title_en', 'Unknown')}*
📺 _{series.get('title_si', 'Unknown')}_

━━━━━━━━━━━━━━━━━━━━

📖 *Description:*
{series.get('description_en', 'No description')[:200]}...

━━━━━━━━━━━━━━━━━━━━

📊 *Info:*
🎭 Genre: {series.get('category', 'N/A')}
📺 Episodes: {series.get('episodes', 0)}
⭐ Rating: {series.get('rating', 0):.1f}/10
👁️ Views: {series.get('views', 0):,}

━━━━━━━━━━━━━━━━━━━━

🎯 *Available:*
💾 720p, 1080p, 4K
🗣️ Sinhala Subtitles

━━━━━━━━━━━━━━━━━━━━
        """
    
    keyboard = [
        [InlineKeyboardButton(f"{E['episode']} Episodes | කථාංග", callback_data=f"eps_{series['series_id']}")],
        [
            InlineKeyboardButton(f"{E['star']} Favorite", callback_data=f"fav_{series['series_id']}"),
            InlineKeyboardButton("📤 Share", switch_inline_query=series.get('title_en', ''))
        ],
        [InlineKeyboardButton(f"{E['back']} Back", callback_data="browse")]
    ]
    
    return text, InlineKeyboardMarkup(keyboard)

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Save user
    await save_user(user)
    
    # Check subscription
    if FORCE_SUBSCRIBE:
        subscribed = await check_subscription(user.id, context)
        if not subscribed:
            keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
            await update.message.reply_text(
                f"{E['warning']} Please join our channel first!\nකරුණාකර පළමුව නාලිකාවට එකතු වන්න!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
    
    # Get user language
    user_data = await get_user_data(user.id)
    lang = user_data.get('language', 'si') if user_data else 'si'
    
    # Send welcome message
    text, keyboard = welcome_message(user.first_name, lang)
    
    try:
        await update.message.reply_photo(
            photo=IMAGES['welcome'],
            caption=text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = f"""
{E['help']} *උදව් / Help*

━━━━━━━━━━━━━━━━━━━━

📌 *විධාන / Commands:*

/start - ආරම්භ කරන්න / Start
/help - උදව් / Help
/search - සොයන්න / Search
/browse - කතා මාලා / Browse
/trending - ජනප්‍රිය / Trending
/stats - සංඛ්‍යා / Statistics
/settings - සැකසුම් / Settings

━━━━━━━━━━━━━━━━━━━━

🔍 *භාවිතය / Usage:*

1️⃣ කතා මාලා සොයන්න:
   /search භාවිතා කරන්න

2️⃣ බාගත කිරීම:
   කතා මාලාවක් තෝරන්න → කථාංගය → Download

3️⃣ ඉල්ලීම්:
   /request භාවිතා කරන්න

━━━━━━━━━━━━━━━━━━━━

💡 *ඉඟි / Tips:*

✅ නාලිකාවට එකතු වන්න
✅ නිතර යාවත්කාලීන
✅ ගුණාත්මක උපසිරැසි

━━━━━━━━━━━━━━━━━━━━
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user = update.effective_user
    user_data = await get_user_data(user.id)
    
    if not user_data:
        await update.message.reply_text("Use /start first")
        return
    
    days = (datetime.now() - user_data['joined_date']).days
    
    stats_text = f"""
📊 *ඔබගේ සංඛ්‍යා / Your Stats*

━━━━━━━━━━━━━━━━━━━━

👤 *User:* {user_data['first_name']}
🆔 *ID:* `{user_data['user_id']}`
📅 *Joined:* {user_data['joined_date'].strftime('%Y-%m-%d')}
⏱️ *Days:* {days}

━━━━━━━━━━━━━━━━━━━━

📥 *Activity:*
⬇️ Downloads: {user_data.get('downloads', 0)}
🔍 Searches: {user_data.get('searches', 0)}
🎮 Points: {user_data.get('points', 0)}
📊 Sessions: {user_data.get('session_count', 0)}

━━━━━━━━━━━━━━━━━━━━
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} No permission!")
        return
    
    admin_text = f"""
{E['admin']} *Admin Panel*

━━━━━━━━━━━━━━━━━━━━

Welcome Admin {user.first_name}!

*Commands:*
/broadcast - විකාශනය
/addcontent - අන්තර්ගතය
/stats - සංඛ්‍යා ලේඛන
/users - පරිශීලකයින්

━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics"),
            InlineKeyboardButton("👥 Users", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton("📝 Add Series", callback_data="admin_addseries"),
            InlineKeyboardButton("📺 Add Episode", callback_data="admin_addepisode")
        ],
        [InlineKeyboardButton(f"{E['back']} Close", callback_data="admin_close")]
    ]
    
    await update.message.reply_text(admin_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================
# CALLBACK HANDLERS
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    
    # Save user activity
    await save_user(user)
    
    # Get user data
    user_data = await get_user_data(user.id)
    lang = user_data.get('language', 'si') if user_data else 'si'
    
    # Main menu
    if data == "main_menu":
        text, keyboard = welcome_message(user.first_name, lang)
        try:
            await query.message.edit_caption(caption=text, parse_mode='Markdown', reply_markup=keyboard)
        except:
            await query.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
    
    # Browse series
    elif data == "browse":
        series_list = await db.db.series.find({'is_active': True}).limit(10).to_list(10)
        
        if not series_list:
            await query.message.reply_text(f"{E['warning']} No series available yet!")
            return
        
        keyboard = []
        for series in series_list:
            emoji = E['new'] if series.get('is_new') else E['fire'] if series.get('is_trending') else E['series']
            keyboard.append([InlineKeyboardButton(
                f"{emoji} {series.get('title_si', series.get('title_en', 'Unknown'))}",
                callback_data=f"series_{series['series_id']}"
            )])
        
        keyboard.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="main_menu")])
        
        text = f"{E['series']} *කතා මාලා / Series*\n\nතෝරන්න / Choose:"
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    
    # View series
    elif data.startswith("series_"):
        series_id = data.replace("series_", "")
        series = await db.db.series.find_one({'series_id': series_id})
        
        if not series:
            await query.message.reply_text(f"{E['error']} Series not found!")
            return
        
        text, keyboard = series_card(series, lang)
        
        image_url = series.get('poster_url', IMAGES['placeholder'])
        try:
            await query.message.reply_photo(
                photo=image_url,
                caption=text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except:
            await query.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)
    
    # View episodes
    elif data.startswith("eps_"):
        series_id = data.replace("eps_", "")
        episodes = await db.db.episodes.find({'series_id': series_id, 'is_active': True}).to_list(100)
        
        if not episodes:
            await query.message.reply_text(f"{E['warning']} No episodes yet!")
            return
        
        keyboard = []
        for ep in episodes:
            ep_text = f"{E['episode']} S{ep.get('season', 1):02d}E{ep.get('episode', 0):02d} - {ep.get('title', 'Episode')}"
            keyboard.append([InlineKeyboardButton(ep_text, callback_data=f"ep_{ep['episode_id']}")])
        
        keyboard.append([InlineKeyboardButton(f"{E['back']} Back", callback_data=f"series_{series_id}")])
        
        await query.message.reply_text(
            f"{E['episode']} *Episodes*\n\nතෝරන්න:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Download episode
    elif data.startswith("ep_"):
        episode_id = data.replace("ep_", "")
        episode = await db.db.episodes.find_one({'episode_id': episode_id})
        
        if not episode:
            await query.message.reply_text(f"{E['error']} Episode not found!")
            return
        
        # Update stats
        await db.db.episodes.update_one({'episode_id': episode_id}, {'$inc': {'downloads': 1}})
        await db.db.users.update_one({'user_id': user.id}, {'$inc': {'downloads': 1, 'points': 5}})
        
        # Send file
        file_id = episode.get('file_id')
        if file_id:
            caption = f"{E['success']} {episode.get('title', 'Episode')}\n\n{E['download']} Download Complete!"
            await query.message.reply_document(document=file_id, caption=caption)
        else:
            await query.message.reply_text(f"{E['error']} File not available!")
    
    # Search
    elif data == "search":
        await query.message.reply_text(
            f"{E['search']} *සෙවීම / Search*\n\nකතා මාලාවේ නම ටයිප් කරන්න:\nType series name:",
            parse_mode='Markdown'
        )
    
    # Trending
    elif data == "trending":
        series_list = await db.db.series.find({'is_trending': True}).limit(10).to_list(10)
        
        if not series_list:
            await query.message.reply_text(f"{E['warning']} No trending series!")
            return
        
        keyboard = []
        for series in series_list:
            keyboard.append([InlineKeyboardButton(
                f"{E['fire']} {series.get('title_si', series.get('title_en', 'Unknown'))}",
                callback_data=f"series_{series['series_id']}"
            )])
        
        keyboard.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="main_menu")])
        
        await query.message.reply_text(
            f"{E['fire']} *Trending Series*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Featured
    elif data == "featured":
        series_list = await db.db.series.find({'is_featured': True}).limit(10).to_list(10)
        
        if not series_list:
            await query.message.reply_text(f"{E['warning']} No featured series!")
            return
        
        keyboard = []
        for series in series_list:
            keyboard.append([InlineKeyboardButton(
                f"{E['star']} {series.get('title_si', series.get('title_en', 'Unknown'))}",
                callback_data=f"series_{series['series_id']}"
            )])
        
        keyboard.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="main_menu")])
        
        await query.message.reply_text(
            f"{E['star']} *Featured Series*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Help
    elif data == "help":
        await help_command(update, context)
    
    # Stats
    elif data == "stats":
        await stats_command(update, context)
    
    # Settings
    elif data == "settings":
        keyboard = [
            [
                InlineKeyboardButton("🌐 සිංහල", callback_data="lang_si"),
                InlineKeyboardButton("🌐 English", callback_data="lang_en")
            ],
            [InlineKeyboardButton(f"{E['back']} Back", callback_data="main_menu")]
        ]
        
        await query.message.reply_text(
            f"{E['settings']} *Settings*\n\nChoose language:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Language change
    elif data.startswith("lang_"):
        new_lang = data.replace("lang_", "")
        await db.db.users.update_one({'user_id': user.id}, {'$set': {'language': new_lang}})
        await query.message.reply_text(f"{E['success']} Language updated!")

# ============================================
# MESSAGE HANDLERS
# ============================================

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search messages"""
    query_text = update.message.text.strip()
    user = update.effective_user
    
    if len(query_text) < 2:
        await update.message.reply_text(f"{E['warning']} Search query too short!")
        return
    
    # Update search count
    await db.db.users.update_one({'user_id': user.id}, {'$inc': {'searches': 1}})
    
    # Search in database
    results = await db.db.series.find({
        '$or': [
            {'title_en': {'$regex': query_text, '$options': 'i'}},
            {'title_si': {'$regex': query_text, '$options': 'i'}}
        ],
        'is_active': True
    }).limit(10).to_list(10)
    
    if not results:
        await update.message.reply_text(
            f"{E['warning']} No results found for '{query_text}'\n\n"
            f"Try different keywords or /browse all series"
        )
        return
    
    # Show results
    keyboard = []
    for series in results:
        keyboard.append([InlineKeyboardButton(
            f"{E['series']} {series.get('title_si', series.get('title_en', 'Unknown'))}",
            callback_data=f"series_{series['series_id']}"
        )])
    
    await update.message.reply_text(
        f"{E['search']} *Search Results* ({len(results)})\n\nතෝරන්න:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# ERROR HANDLER
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                f"{E['error']} දෝෂයක් සිදුවිය / Error occurred\n\n"
                f"Please try again or contact admin"
            )
        except:
            pass

# ============================================
# INITIALIZATION
# ============================================

async def post_init(app: Application):
    """Initialize bot"""
    logger.info("🚀 Starting bot...")
    
    # Connect to database
    connected = await db.connect()
    if not connected:
        logger.error("❌ Database connection failed!")
        return
    
    # Set commands
    commands = [
        ("start", "Start bot | ආරම්භ කරන්න"),
        ("help", "Help | උදව්"),
        ("search", "Search | සොයන්න"),
        ("browse", "Browse | කතා මාලා"),
        ("trending", "Trending | ජනප්‍රිය"),
        ("stats", "Statistics | සංඛ්‍යා"),
        ("settings", "Settings | සැකසුම්"),
        ("admin", "Admin | පරිපාලක")
    ]
    
    await app.bot.set_my_commands(commands)
    logger.info("✅ Bot started successfully!")

async def post_shutdown(app: Application):
    """Cleanup on shutdown"""
    await db.disconnect()
    logger.info("✅ Bot stopped")

# ============================================
# MAIN
# ============================================

def main():
    """Run bot"""
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    app.add_error_handler(error_handler)
    
    # Run bot
    logger.info("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
