"""
🎬 SINHALA SUBTITLE BOT - ULTRA PRO V2
සිංහල උපසිරැසි බොට් - සම්පූර්ණ ක්‍රියාකාරී bot එකක්

🆕 New Features:
- Auto file indexing from channel
- Bot mention reply
- Contact system with buttons
- Request system with admin approval
- Enhanced stats display
- Duplicate file removal
- Improved broadcast system
- Pagination support
"""

import os
import re
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'sinhala_sub_bot')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
CHANNEL_ID = os.getenv('CHANNEL_ID', '')  # Main channel for file indexing
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@YourChannel')
FORCE_SUBSCRIBE = os.getenv('FORCE_SUBSCRIBE', 'true').lower() == 'true'
REQUEST_CHANNEL_ID = os.getenv('REQUEST_CHANNEL_ID', '')  # Admin channel for requests
BOT_USERNAME = os.getenv('BOT_USERNAME', 'YourBot')

# Contact info (can be set via environment or changed here)
DEVELOPER_LINK = os.getenv('DEVELOPER_LINK', 'https://t.me/YourDeveloper')
OWNER_LINK = os.getenv('OWNER_LINK', 'https://t.me/YourOwner')
OWNER_WHATSAPP = os.getenv('OWNER_WHATSAPP', 'https://wa.me/94701234567')

# Emojis
E = {
    'series': '🎬', 'episode': '📺', 'download': '⬇️', 'search': '🔍',
    'back': '🔙', 'home': '🏠', 'settings': '⚙️', 'help': 'ℹ️',
    'success': '✅', 'error': '❌', 'warning': '⚠️', 'loading': '🔄',
    'star': '⭐', 'fire': '🔥', 'new': '🆕', 'admin': '👑',
    'contact': '📞', 'request': '📝'
}

# Conversation states
AWAITING_REQUEST_NAME = 1
AWAITING_REQUEST_YEAR = 2
AWAITING_BROADCAST_MESSAGE = 3

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
        await self.db.files.create_index("file_id", unique=True)
        await self.db.files.create_index("file_unique_id", unique=True)
        await self.db.files.create_index([("file_name", "text"), ("caption", "text")])
        await self.db.searches.create_index("user_id")
        await self.db.searches.create_index("timestamp")
        await self.db.requests.create_index("user_id")
        await self.db.requests.create_index("status")
    
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
                    }
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
                'searches_count': 0,
                'language': 'si'
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

async def save_file_index(message: Message):
    """Index file from channel to database"""
    try:
        # Get file info based on message type
        file_obj = None
        file_type = None
        
        if message.document:
            file_obj = message.document
            file_type = 'document'
        elif message.video:
            file_obj = message.video
            file_type = 'video'
        elif message.audio:
            file_obj = message.audio
            file_type = 'audio'
        elif message.photo:
            file_obj = message.photo[-1]  # Get largest photo
            file_type = 'photo'
        else:
            return False
        
        # Check if already indexed
        existing = await db.db.files.find_one({'file_unique_id': file_obj.file_unique_id})
        if existing:
            logger.info(f"File already indexed: {file_obj.file_unique_id}")
            return False
        
        # Get file name
        file_name = getattr(file_obj, 'file_name', None) or message.caption or 'Unnamed'
        
        # Create file document
        file_doc = {
            'file_id': file_obj.file_id,
            'file_unique_id': file_obj.file_unique_id,
            'file_name': file_name,
            'file_type': file_type,
            'file_size': getattr(file_obj, 'file_size', 0),
            'mime_type': getattr(file_obj, 'mime_type', None),
            'caption': message.caption or '',
            'message_id': message.message_id,
            'chat_id': message.chat_id,
            'date': message.date,
            'indexed_date': datetime.now()
        }
        
        await db.db.files.insert_one(file_doc)
        logger.info(f"✅ Indexed: {file_name} ({file_type})")
        return True
        
    except Exception as e:
        logger.error(f"Error indexing file: {e}")
        return False

def get_file_hash(file_id: str, file_size: int) -> str:
    """Generate hash for duplicate detection"""
    return hashlib.md5(f"{file_id}{file_size}".encode()).hexdigest()

# ============================================
# MESSAGE TEMPLATES
# ============================================

def welcome_message(name: str):
    """Generate welcome message"""
    text = f"""
{E['series']} *සුභ පැතුම් {name}!* 🇱🇰

┏━━━━━━━━━━━━━━━━━━━━┓
┃  *SINHALA SUB BOT*  ┃
┗━━━━━━━━━━━━━━━━━━━━┛

{E['star']} *අපගේ විශේෂාංග:*

📚 විශාල file එකතුවක්
{E['search']} පහසු සෙවීම - ක්ෂණික ප්‍රතිඵල
⚡ වේගවත් බාගත කිරීම
💎 SRT, ZIP, RAR සහ සියලු formats

━━━━━━━━━━━━━━━━━━━━
{E['help']} *ආරම්භ කරන්න:*
පහත බොත්තම් ඔබන්න 👇
    """
    
    keyboard = [
        [
            InlineKeyboardButton(f"{E['search']} Search | සොයන්න", callback_data="search")
        ],
        [
            InlineKeyboardButton(f"{E['request']} Request | ඉල්ලීමක්", callback_data="request"),
            InlineKeyboardButton(f"{E['contact']} Contact | සම්බන්ධ", callback_data="contact")
        ],
        [
            InlineKeyboardButton("📊 Stats | සංඛ්‍යා", callback_data="stats"),
            InlineKeyboardButton(f"{E['help']} Help | උදව්", callback_data="help")
        ]
    ]
    
    if CHANNEL_USERNAME:
        keyboard.append([
            InlineKeyboardButton(f"📢 Join Channel | නාලිකාව", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        ])
    
    return text, InlineKeyboardMarkup(keyboard)

def contact_message():
    """Generate contact message"""
    text = f"""
{E['contact']} *සම්බන්ධ වන්න / Contact Us*

━━━━━━━━━━━━━━━━━━━━

Bot ගේ මොකක් හරි අවුලක් තිබ්බොතින් හරි, දැනගන්න ඕන දෙයක් තිබ්බොත් හරි, අනිවාරෙන් Message එකක් දාන්න.... 😇

🍀🍀🍀🍀🍀🍀🍀🍀🍀

ඔබගේ ව්‍යාපාරයේ Business මදි නිසා පසුතැවෙනවද ? 😐

Website එකක් ගහලා Business එක Up කරලා ගමුද ? 😏

ඔබගේ එදිනෙදා වැඩ කටයුතු පහසු කර ගැනීමට Telegram Bot කෙනෙක් හදාගන්න කැමතිද ?

ඉතාම සාධාරණ අඩු මුදලකට ඔබගේ ව්‍යාපාරයට අවශ්‍ය Websites, Telegram bots, Telegram Userbots සාදා ගැනීමට අවශ්‍ය නම් පහත Contacts වලින් සම්බන්ධ වන්න...😇

━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_LINK)],
        [InlineKeyboardButton("👑 Owner", url=OWNER_LINK)],
        [InlineKeyboardButton("📱 Owner WhatsApp", url=OWNER_WHATSAPP)],
        [InlineKeyboardButton(f"{E['back']} Back | ආපසු", callback_data="main_menu")]
    ]
    
    return text, InlineKeyboardMarkup(keyboard)

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await save_user(user)
    
    # Check subscription
    if not await check_subscription(user.id, context):
        keyboard = [[InlineKeyboardButton(
            f"📢 Join Channel | නාලිකාව එකට Join වෙන්න",
            url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
        )]]
        await update.message.reply_text(
            f"{E['warning']} *කරුණාකර මුලින්ම Channel එකට Join වෙන්න!*\n\n"
            f"Please join our channel first!\n\n"
            f"Join කළ පසු /start ආපසු යොදන්න",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    text, keyboard = welcome_message(user.first_name)
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = f"""
{E['help']} *උදව් / Help*

━━━━━━━━━━━━━━━━━━━━

*භාවිතා කරන්නේ කෙසේද:*

1️⃣ {E['search']} *සෙවීම:*
   Film එකේ නම හෝ කොටසක් type කරන්න

2️⃣ {E['request']} *ඉල්ලීමක්:*
   /request - නව film එකක් request කරන්න

3️⃣ {E['contact']} *සම්බන්ධ:*
   /contact - අප සමඟ සම්බන්ධ වන්න

4️⃣ 📊 *සංඛ්‍යා:*
   /stats - Bot statistics බලන්න

━━━━━━━━━━━━━━━━━━━━

*Admin Commands:*
/broadcast - Message යවන්න
/deleteduplicates - Duplicate files ඉවත් කරන්න
/indexstats - Indexing statistics

━━━━━━━━━━━━━━━━━━━━

{E['success']} Bot නම mention කළත් search වෙනවා!
Example: @{BOT_USERNAME} breaking bad
    """
    
    keyboard = [[InlineKeyboardButton(f"{E['back']} Back | ආපසු", callback_data="main_menu")]]
    
    if update.callback_query:
        await update.callback_query.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced stats display"""
    try:
        # Get counts
        total_users = await db.db.users.count_documents({})
        thirty_days_ago = datetime.now() - timedelta(days=30)
        monthly_active = await db.db.users.count_documents({'last_active': {'$gte': thirty_days_ago}})
        
        # Get chat stats
        channels = await db.db.chats.count_documents({'type': 'channel'})
        groups = await db.db.chats.count_documents({'type': {'$in': ['group', 'supergroup']}})
        total_chats = channels + groups
        
        # Get search and file stats
        total_searches = await db.db.searches.count_documents({})
        indexed_files = await db.db.files.count_documents({})
        
        stats_text = f"""
📊 *Bot Statistics*

━━━━━━━━━━━━━━━━━━━━

👥 *Users:*
├ Total Users: *{total_users:,}*
└ Monthly Active: *{monthly_active:,}*

━━━━━━━━━━━━━━━━━━━━

📢 *Chats:*
├ Channels Added: *{channels:,}*
├ Groups Added: *{groups:,}*
└ Total Chats: *{total_chats:,}*

━━━━━━━━━━━━━━━━━━━━

🔍 *Activity:*
├ Total Searches: *{total_searches:,}*
└ Indexed Files: *{indexed_files:,}*

━━━━━━━━━━━━━━━━━━━━

⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        keyboard = [[InlineKeyboardButton(f"{E['back']} Back | ආපසු", callback_data="main_menu")]]
        
        if update.callback_query:
            await update.callback_query.message.reply_text(
                stats_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                stats_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        logger.error(f"Stats error: {e}")
        error_msg = f"{E['error']} Error fetching stats!"
        if update.callback_query:
            await update.callback_query.message.reply_text(error_msg)
        else:
            await update.message.reply_text(error_msg)

# ============================================
# REQUEST SYSTEM
# ============================================

async def request_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start request conversation"""
    user = update.effective_user
    await save_user(user)
    
    text = f"""
{E['request']} *Film Request*

━━━━━━━━━━━━━━━━━━━━

කරුණාකර Film එකේ නම ඉංග්‍රීසියෙන් type කරන්න:

*Example:*
Breaking Bad
The Walking Dead
Game of Thrones

━━━━━━━━━━━━━━━━━━━━

/cancel - Cancel කරන්න
    """
    
    if update.callback_query:
        await update.callback_query.message.reply_text(text, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, parse_mode='Markdown')
    
    return AWAITING_REQUEST_NAME

async def request_receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive film name"""
    context.user_data['request_name'] = update.message.text.strip()
    
    text = f"""
{E['request']} *Film Request*

━━━━━━━━━━━━━━━━━━━━

Film: *{context.user_data['request_name']}*

දැන් Film එකේ වර්ෂය type කරන්න:

*Example:*
2020
2019-2023 (for series)

━━━━━━━━━━━━━━━━━━━━

/cancel - Cancel කරන්න
    """
    
    await update.message.reply_text(text, parse_mode='Markdown')
    return AWAITING_REQUEST_YEAR

async def request_receive_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive year and save request"""
    user = update.effective_user
    year = update.message.text.strip()
    film_name = context.user_data.get('request_name', '')
    
    # Save request to database
    request_doc = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'film_name': film_name,
        'year': year,
        'status': 'pending',
        'request_date': datetime.now()
    }
    
    result = await db.db.requests.insert_one(request_doc)
    request_id = str(result.inserted_id)
    
    # Send to user
    await update.message.reply_text(
        f"{E['success']} *Request එක යවා ඇත!*\n\n"
        f"📝 Film: *{film_name}*\n"
        f"📅 Year: *{year}*\n\n"
        f"Admin team එක ඉක්මනින් review කරයි! 😊",
        parse_mode='Markdown'
    )
    
    # Send to admin channel
    if REQUEST_CHANNEL_ID:
        admin_text = f"""
{E['new']} *New Request*

━━━━━━━━━━━━━━━━━━━━

👤 User: {user.first_name} (@{user.username or 'N/A'})
🆔 User ID: `{user.id}`

📝 Film: *{film_name}*
📅 Year: *{year}*

━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Done", callback_data=f"req_done_{request_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"req_no_{request_id}")
            ]
        ]
        
        try:
            await context.bot.send_message(
                chat_id=REQUEST_CHANNEL_ID,
                text=admin_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error sending to admin channel: {e}")
    
    context.user_data.clear()
    return ConversationHandler.END

async def request_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel request"""
    await update.message.reply_text(f"{E['error']} Request cancelled!")
    context.user_data.clear()
    return ConversationHandler.END

# ============================================
# SEARCH HANDLER
# ============================================

async def search_files(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str, page: int = 0):
    """Search files with pagination"""
    user = update.effective_user
    await save_user(user)
    
    # Save search query
    await db.db.searches.insert_one({
        'user_id': user.id,
        'query': query,
        'timestamp': datetime.now()
    })
    
    # Increment user search count
    await db.db.users.update_one({'user_id': user.id}, {'$inc': {'searches_count': 1}})
    
    # Search in database
    search_regex = {'$regex': query, '$options': 'i'}
    results = await db.db.files.find({
        '$or': [
            {'file_name': search_regex},
            {'caption': search_regex}
        ]
    }).sort('indexed_date', -1).to_list(None)
    
    if not results:
        await update.message.reply_text(
            f"{E['warning']} '{query}' සඳහා ප්‍රතිඵල හමු නොවීය!\n\n"
            f"No results found for '{query}'\n\n"
            f"Try different keywords or /request a new film"
        )
        return
    
    # Pagination - 10 results per page
    per_page = 10
    total_pages = (len(results) - 1) // per_page + 1
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(results))
    page_results = results[start_idx:end_idx]
    
    # Build keyboard
    keyboard = []
    for file_doc in page_results:
        file_name = file_doc.get('file_name', 'Unknown')
        file_type = file_doc.get('file_type', 'file')
        
        # Truncate long names
        if len(file_name) > 50:
            file_name = file_name[:47] + '...'
        
        btn_text = f"📄 {file_name}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"file_{file_doc['_id']}")])
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"search_page_{query}_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"search_page_{query}_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(f"{E['home']} Main Menu", callback_data="main_menu")])
    
    result_text = f"""
{E['search']} *Search Results*

Query: `{query}`
Found: *{len(results)}* files
Page: *{page + 1}/{total_pages}*

━━━━━━━━━━━━━━━━━━━━

Select a file below 👇
    """
    
    await update.message.reply_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    text = update.message.text.strip()
    
    # Check if message is from channel and is a file
    if update.message.chat.type == 'channel':
        if any([update.message.document, update.message.video, update.message.audio, update.message.photo]):
            await save_file_index(update.message)
        return
    
    # Bot mention check
    if BOT_USERNAME and f"@{BOT_USERNAME}" in text:
        # Extract search query (remove bot mention)
        query = text.replace(f"@{BOT_USERNAME}", "").strip()
        if len(query) >= 2:
            await search_files(update, context, query)
        return
    
    # Regular search
    if len(text) >= 2:
        await search_files(update, context, text)

# ============================================
# CALLBACK HANDLERS
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    
    # Main menu
    if data == "main_menu":
        text, keyboard = welcome_message(user.first_name)
        await query.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
    
    # Search
    elif data == "search":
        await query.message.reply_text(
            f"{E['search']} *සෙවීම / Search*\n\n"
            f"Film එකේ නම හෝ කොටසක් type කරන්න:\n"
            f"Type film name or part of it:",
            parse_mode='Markdown'
        )
    
    # Contact
    elif data == "contact":
        text, keyboard = contact_message()
        await query.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
    
    # Request
    elif data == "request":
        await request_start(update, context)
    
    # Stats
    elif data == "stats":
        await stats_command(update, context)
    
    # Help
    elif data == "help":
        await help_command(update, context)
    
    # File download
    elif data.startswith("file_"):
        from bson import ObjectId
        file_id = data.replace("file_", "")
        
        try:
            file_doc = await db.db.files.find_one({'_id': ObjectId(file_id)})
            
            if not file_doc:
                await query.message.reply_text(f"{E['error']} File not found!")
                return
            
            # Send file based on type
            file_telegram_id = file_doc.get('file_id')
            caption = file_doc.get('caption', '') or file_doc.get('file_name', '')
            
            if file_doc['file_type'] == 'document':
                await query.message.reply_document(document=file_telegram_id, caption=caption)
            elif file_doc['file_type'] == 'video':
                await query.message.reply_video(video=file_telegram_id, caption=caption)
            elif file_doc['file_type'] == 'audio':
                await query.message.reply_audio(audio=file_telegram_id, caption=caption)
            elif file_doc['file_type'] == 'photo':
                await query.message.reply_photo(photo=file_telegram_id, caption=caption)
            
            # Update download count
            await db.db.files.update_one({'_id': ObjectId(file_id)}, {'$inc': {'downloads': 1}})
            
        except Exception as e:
            logger.error(f"Error sending file: {e}")
            await query.message.reply_text(f"{E['error']} Error sending file!")
    
    # Request response (admin)
    elif data.startswith("req_"):
        if user.id not in ADMIN_IDS:
            await query.answer("Not authorized!", show_alert=True)
            return
        
        from bson import ObjectId
        parts = data.split("_")
        action = parts[1]  # done or no
        request_id = parts[2]
        
        try:
            request_doc = await db.db.requests.find_one({'_id': ObjectId(request_id)})
            
            if not request_doc:
                await query.answer("Request not found!", show_alert=True)
                return
            
            # Update request status
            new_status = 'completed' if action == 'done' else 'rejected'
            await db.db.requests.update_one(
                {'_id': ObjectId(request_id)},
                {'$set': {'status': new_status, 'updated_date': datetime.now()}}
            )
            
            # Send response to user
            user_id = request_doc['user_id']
            film_name = request_doc['film_name']
            
            if action == 'done':
                user_msg = (
                    f"{E['success']} *Request Completed!*\n\n"
                    f"Your request for *{film_name}* has been completed!\n"
                    f"Check the channel for the file. 😊"
                )
            else:
                user_msg = (
                    f"{E['warning']} *Request Update*\n\n"
                    f"Your request for *{film_name}* could not be completed at this time.\n"
                    f"Please try again later or contact admin."
                )
            
            try:
                await context.bot.send_message(chat_id=user_id, text=user_msg, parse_mode='Markdown')
            except:
                pass
            
            # Update admin message
            await query.message.edit_text(
                query.message.text + f"\n\n{E['success']} Status: *{new_status.upper()}*",
                parse_mode='Markdown'
            )
            await query.answer(f"Request marked as {new_status}!")
            
        except Exception as e:
            logger.error(f"Error processing request response: {e}")
            await query.answer("Error processing request!", show_alert=True)
    
    # Pagination
    elif data.startswith("search_page_"):
        parts = data.replace("search_page_", "").rsplit("_", 1)
        query_text = parts[0]
        page = int(parts[1])
        
        # Create fake update for search
        update.message = query.message
        await search_files(update, context, query_text, page)

# ============================================
# ADMIN COMMANDS
# ============================================

async def delete_duplicates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete duplicate files"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} No permission!")
        return
    
    await update.message.reply_text(f"{E['loading']} Checking for duplicates...")
    
    try:
        # Find duplicates by file_unique_id
        pipeline = [
            {
                '$group': {
                    '_id': '$file_unique_id',
                    'count': {'$sum': 1},
                    'ids': {'$push': '$_id'}
                }
            },
            {
                '$match': {
                    'count': {'$gt': 1}
                }
            }
        ]
        
        duplicates = await db.db.files.aggregate(pipeline).to_list(None)
        
        if not duplicates:
            await update.message.reply_text(f"{E['success']} No duplicates found!")
            return
        
        deleted_count = 0
        for dup in duplicates:
            # Keep first, delete rest
            ids_to_delete = dup['ids'][1:]
            result = await db.db.files.delete_many({'_id': {'$in': ids_to_delete}})
            deleted_count += result.deleted_count
        
        await update.message.reply_text(
            f"{E['success']} Deleted *{deleted_count}* duplicate files!\n"
            f"Found *{len(duplicates)}* duplicate groups.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error deleting duplicates: {e}")
        await update.message.reply_text(f"{E['error']} Error: {e}")

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} No permission!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📢 *Broadcast Message*\n\n"
        "Send me the message to broadcast:\n"
        "- You can send text, photo, video, document\n"
        "- You can forward a message\n"
        "- Buttons will be preserved\n\n"
        "/cancel to cancel",
        parse_mode='Markdown'
    )
    
    return AWAITING_BROADCAST_MESSAGE

async def broadcast_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and broadcast message"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        return ConversationHandler.END
    
    # Store message for broadcasting
    context.user_data['broadcast_message'] = update.message
    
    users = await db.db.users.find({}).to_list(None)
    
    await update.message.reply_text(
        f"📢 Broadcasting to *{len(users)}* users...\n"
        f"This may take a few minutes.",
        parse_mode='Markdown'
    )
    
    sent = 0
    failed = 0
    message_to_broadcast = context.user_data['broadcast_message']
    
    for user_data in users:
        try:
            await message_to_broadcast.copy(chat_id=user_data['user_id'])
            sent += 1
        except Exception as e:
            failed += 1
            logger.debug(f"Failed to send to {user_data['user_id']}: {e}")
    
    await update.message.reply_text(
        f"{E['success']} *Broadcast Complete!*\n\n"
        f"✅ Sent: *{sent}*\n"
        f"❌ Failed: *{failed}*",
        parse_mode='Markdown'
    )
    
    context.user_data.clear()
    return ConversationHandler.END

# ============================================
# CHANNEL POST HANDLER
# ============================================

async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle channel posts for file indexing"""
    message = update.channel_post
    
    # Check if it's from our main channel
    if str(message.chat_id) == CHANNEL_ID or (CHANNEL_USERNAME and message.chat.username == CHANNEL_USERNAME.replace('@', '')):
        # Index file if present
        if any([message.document, message.video, message.audio, message.photo]):
            await save_file_index(message)
            
            # Save chat info
            await db.db.chats.update_one(
                {'chat_id': message.chat_id},
                {
                    '$set': {
                        'chat_id': message.chat_id,
                        'title': message.chat.title,
                        'username': message.chat.username,
                        'type': message.chat.type,
                        'last_updated': datetime.now()
                    }
                },
                upsert=True
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
                f"Please try again or /contact admin"
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
        ("request", "Request | ඉල්ලීමක්"),
        ("contact", "Contact | සම්බන්ධ"),
        ("stats", "Statistics | සංඛ්‍යා"),
        ("deleteduplicates", "Delete duplicates (Admin)"),
        ("broadcast", "Broadcast (Admin)")
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
    
    # Request conversation handler
    request_conv = ConversationHandler(
        entry_points=[
            CommandHandler('request', request_start),
            CallbackQueryHandler(request_start, pattern="^request$")
        ],
        states={
            AWAITING_REQUEST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_receive_name)],
            AWAITING_REQUEST_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_receive_year)]
        },
        fallbacks=[CommandHandler('cancel', request_cancel)]
    )
    
    # Broadcast conversation handler
    broadcast_conv = ConversationHandler(
        entry_points=[CommandHandler('broadcast', broadcast_start)],
        states={
            AWAITING_BROADCAST_MESSAGE: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_receive)]
        },
        fallbacks=[CommandHandler('cancel', request_cancel)]
    )
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("contact", lambda u, c: c.bot.send_message(u.effective_chat.id, *contact_message())))
    app.add_handler(CommandHandler("deleteduplicates", delete_duplicates))
    app.add_handler(request_conv)
    app.add_handler(broadcast_conv)
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.CHANNEL_POST, channel_post_handler))
    app.add_error_handler(error_handler)
    
    # Run bot
    logger.info("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
