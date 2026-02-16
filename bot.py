"""
🎬 SINHALA SUBTITLE BOT - ULTRA PRO V2 - ENHANCED
සිංහල උපසිරැසි බොට් - සම්පූර්ණ ක්‍රියාකාරී bot එකක්

✨ Enhanced Features:
- Auto file indexing from channel with beautiful captions
- Ban/Unban system with username or ID
- Enhanced broadcast with confirmation
- Forward message support in broadcast
- Fixed pagination (Next/Back buttons)
- Menu banners with images
- Beautiful formatting with emojis
- NO force subscription
"""

import os
import re
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto
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

BOT_TOKEN = os.getenv('BOT_TOKEN', '8502581099:AAHaEU3igT71rRs4NHShTNgcb-6FxmoQXe8')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://Sadisa:JRGgclOXbm5KLiHn@cluster0.vexxjgb.mongodb.net/')
DB_NAME = os.getenv('DB_NAME', 'sinhala_sub_bot')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '8107411538,7001801397').split(',') if x]
CHANNEL_ID = os.getenv('CHANNEL_ID', '-1003839839205')  # Main channel for file indexing
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@YourChannel')
FORCE_SUBSCRIBE = False  # Force subscription disabled
REQUEST_CHANNEL_ID = os.getenv('REQUEST_CHANNEL_ID', '-1003715480267')  # Admin channel for requests
BOT_USERNAME = os.getenv('BOT_USERNAME', '@MySubTest1_bot')

# Contact info
DEVELOPER_NAME = os.getenv('DEVELOPER_NAME', 'Sadesha Hansana')
OWNER_NAME = os.getenv('OWNER_NAME', 'Sadisa Harshana')
DEVELOPER_LINK = os.getenv('DEVELOPER_LINK', 'https://t.me/SadeshaHansana2')
OWNER_LINK = os.getenv('OWNER_LINK', 'https://t.me/sljohnwick')
OWNER_WHATSAPP = os.getenv('OWNER_WHATSAPP', 'https://wa.me/94701234567')

# Menu Banner Images - Upload images to Telegram and use file_id or Telegraph URLs
BANNER_START = os.getenv('BANNER_START', 'https://t.me/shprofilterupdate/300')
BANNER_HELP = os.getenv('BANNER_HELP', 'https://t.me/shprofilterupdate/301')
BANNER_CONTACT = os.getenv('BANNER_CONTACT', 'https://t.me/shprofilterupdate/300')
BANNER_SEARCH = os.getenv('BANNER_SEARCH', 'https://telegra.ph/file/d4f3e965e965e3dfb5b45.jpg')

# Emojis
E = {
    'series': '🎬', 'episode': '📺', 'download': '⬇️', 'search': '🔍',
    'back': '🔙', 'home': '🏠', 'settings': '⚙️', 'help': 'ℹ️',
    'success': '✅', 'error': '❌', 'warning': '⚠️', 'loading': '🔄',
    'star': '⭐', 'fire': '🔥', 'new': '🆕', 'admin': '👑',
    'contact': '📞', 'request': '📝', 'title': '📁', 'year': '🔎', 
    'size': '💾', 'bot': '🤖', 'dev': '🧑‍💻', 'owner': '🙎‍♂️'
}

# Conversation states
AWAITING_REQUEST_NAME = 1
AWAITING_REQUEST_YEAR = 2
AWAITING_BROADCAST_MESSAGE = 3
AWAITING_BROADCAST_CONFIRM = 4

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
        await self.db.banned_users.create_index("user_id", unique=True)
    
    async def disconnect(self):
        if self.client:
            self.client.close()

# Global database instance
db = Database()

# ============================================
# BAN/UNBAN HELPER FUNCTIONS
# ============================================

async def is_user_banned(user_id: int) -> bool:
    """Check if user is banned"""
    try:
        banned = await db.db.banned_users.find_one({'user_id': user_id})
        return banned is not None
    except Exception as e:
        logger.error(f"Error checking ban status: {e}")
        return False

async def ban_user(user_id: int, banned_by: int, reason: str = "No reason"):
    """Ban a user"""
    try:
        await db.db.banned_users.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'user_id': user_id,
                    'banned_by': banned_by,
                    'banned_at': datetime.now(),
                    'reason': reason
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        return False

async def unban_user(user_id: int) -> bool:
    """Unban a user"""
    try:
        result = await db.db.banned_users.delete_one({'user_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        return False

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

def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def extract_title_year_from_filename(filename: str):
    """Extract title and year from filename"""
    # Try to extract year
    year_match = re.search(r'\b(19|20)\d{2}\b', filename)
    year = year_match.group(0) if year_match else "N/A"
    
    # Clean up title
    title = re.sub(r'\.(mkv|mp4|avi|srt|zip|rar)$', '', filename, flags=re.IGNORECASE)
    title = re.sub(r'\b(19|20)\d{2}\b', '', title)
    title = re.sub(r'[._-]', ' ', title).strip()
    
    return title, year

def create_file_caption(file_name: str, file_size: int) -> str:
    """Create beautiful caption for file"""
    title, year = extract_title_year_from_filename(file_name)
    size_str = format_file_size(file_size)
    
    caption = f"""
{E['title']}𝗧𝗶𝘁𝗹𝗲  - {title}
{E['year']}𝗬𝗲𝗮𝗿  - {year}
{E['size']}𝗦𝗶𝘇𝗲   - {size_str}

𝗦𝗜𝗡𝗛𝗔𝗟𝗔  𝗦𝗨𝗕𝗧𝗜𝗧𝗟𝗘  𝗕𝗢𝗧
{E['dev']}𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐝 𝐁𝐲 - 𝗦𝗮𝗱𝗲𝘀𝗵𝗮 𝗛𝗮𝗻𝘀𝗮𝗻𝗮
{E['owner']}𝐏𝐫𝐨𝐝𝐮𝐬𝐞 𝐀𝐧𝐝 𝐎𝐰𝐧𝐞𝐫 - 𝗦𝗮𝗱𝗶𝘀𝗮 𝗛𝗮𝗿𝘀𝗵𝗮𝗻𝗮
"""
    return caption.strip()

def get_file_hash(file_id: str, file_size: int) -> str:
    """Generate hash for duplicate detection"""
    return hashlib.md5(f"{file_id}{file_size}".encode()).hexdigest()

# ============================================
# MESSAGE TEMPLATES
# ============================================

def welcome_message(name: str):
    """Generate welcome message"""
    text = f"""
╔═══════════════════════════╗
║  {E['series']} 𝗦𝗜𝗡𝗛𝗔𝗟𝗔 𝗦𝗨𝗕 𝗕𝗢𝗧  ║
╚═══════════════════════════╝

{E['fire']} **සුභ පැතුම් {name}!** 🇱🇰

━━━━━━━━━━━━━━━━━━━━━━━━━━
{E['star']} **අපගේ විශේෂාංග:**
━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 විශාල file එකතුවක්
{E['search']} පහසු සෙවීම - ක්ෂණික ප්‍රතිඵල
⚡ වේගවත් බාගත කිරීම
{E['new']} නව files දිනපතා එකතු වේ
{E['download']} උපසිරැසි සහ videos/series

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **භාවිතා කරන්නේ කෙසේද?**
━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 Movie/Series නම ටයිප් කරන්න
🔹 Button මත click කරන්න
🔹 File එක බාගන්න

━━━━━━━━━━━━━━━━━━━━━━━━━━

{E['help']} /help - සම්පූර්ණ උදව්
{E['search']} /search - සෙවීම් පටිගත කරන්න
{E['request']} /request - ඉල්ලීමක් කරන්න
{E['contact']} /contact - අප හා සම්බන්ධ වන්න

━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ ආරම්භ කරමු! Movie/Series නමක් ටයිප් කරන්න
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [
            InlineKeyboardButton(f"{E['help']} උදව්", callback_data="help"),
            InlineKeyboardButton(f"{E['search']} සොයන්න", callback_data="search")
        ],
        [
            InlineKeyboardButton(f"{E['request']} ඉල්ලීමක්", callback_data="request"),
            InlineKeyboardButton(f"{E['contact']} සම්බන්ධ", callback_data="contact")
        ]
    ]
    
    return text, InlineKeyboardMarkup(keyboard)

def help_message():
    """Generate help message"""
    text = f"""
╔═══════════════════════════╗
║   {E['help']} 𝗛𝗘𝗟𝗣 & 𝗚𝗨𝗜𝗗𝗘   ║
╚═══════════════════════════╝

{E['star']} **උදව් මාර්ගෝපදේශය** {E['star']}

━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 **භාවිතා කරන්නේ කෙසේද?**
━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ **සෙවීම:**
   • Movie/Series නම ටයිප් කරන්න
   • උදා: "Avatar", "Money Heist"
   • උදා: "Spiderman 2021"

2️⃣ **Download කිරීම:**
   • ප්‍රතිඵල වලින් button click කරන්න
   • File එක ලැබේ

3️⃣ **ඉල්ලීමක් කිරීම:**
   • /request command එක භාවිතා කරන්න
   • Movie/Series නම හා වසර ඇතුලත් කරන්න

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ **Commands**
━━━━━━━━━━━━━━━━━━━━━━━━━━

/start - Bot ආරම්භ කරන්න
/help - උදව් පණිවිඩය
/search - සෙවීම් පටිගත කරන්න
/request - ඉල්ලීමක් කරන්න
/contact - සම්බන්ධ වන්න
/stats - සංඛ්‍යාලේඛන බලන්න

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **ප්‍රයෝජනවත් Tips:**
━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ නිවැරදි spelling භාවිතා කරන්න
✅ වසර එකතු කරන්න හොඳ ප්‍රතිඵල සඳහා
✅ ඉංග්‍රීසි නම් භාවිතා කරන්න

━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [
            InlineKeyboardButton(f"{E['home']} මුල් පිටුව", callback_data="start"),
            InlineKeyboardButton(f"{E['contact']} සම්බන්ධ", callback_data="contact")
        ]
    ]
    
    return text, InlineKeyboardMarkup(keyboard)

def contact_message():
    """Generate contact message"""
    text = f"""
╔═══════════════════════════╗
║  {E['contact']} 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗨𝗦  ║
╚═══════════════════════════╝

{E['fire']} **අප හා සම්බන්ධ වන්න** {E['fire']}

━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍💻 **Developer:**
{E['dev']} {DEVELOPER_NAME}

👤 **Owner:**
{E['owner']} {OWNER_NAME}

━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 **ප්‍රශ්න, යෝජනා හෝ ගැටළු සඳහා:**
━━━━━━━━━━━━━━━━━━━━━━━━━━

• Bug reports
• Feature requests
• File requests
• Technical support
• Advertising

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ අපි ඉක්මනින් ප්‍රතිචාර දක්වන්නෙමු!
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [
            InlineKeyboardButton(f"{E['dev']} Developer", url=DEVELOPER_LINK),
            InlineKeyboardButton(f"{E['owner']} Owner", url=OWNER_LINK)
        ],
        [
            InlineKeyboardButton("📱 WhatsApp", url=OWNER_WHATSAPP)
        ],
        [
            InlineKeyboardButton(f"{E['back']} ආපසු", callback_data="start")
        ]
    ]
    
    return text, InlineKeyboardMarkup(keyboard)

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    
    # Check if banned
    if await is_user_banned(user.id):
        await update.message.reply_text(
            f"{E['error']} **ඔබව තහනම් කර ඇත!**\n\n"
            f"ඔබට මෙම bot එක භාවිතා කිරීමට අවසර නැත.\n"
            f"වැඩි විස්තර සඳහා /contact භාවිතා කරන්න.",
            parse_mode='Markdown'
        )
        return
    
    await save_user(user)
    
    text, keyboard = welcome_message(user.first_name)
    
    try:
        # Send with banner image
        await update.message.reply_photo(
            photo=BANNER_START,
            caption=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except:
        # Fallback if image fails
        await update.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    user = update.effective_user
    
    # Check if banned
    if await is_user_banned(user.id):
        await update.message.reply_text(
            f"{E['error']} ඔබව තහනම් කර ඇත!",
            parse_mode='Markdown'
        )
        return
    
    text, keyboard = help_message()
    
    try:
        await update.message.reply_photo(
            photo=BANNER_HELP,
            caption=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contact command handler"""
    user = update.effective_user
    
    # Check if banned
    if await is_user_banned(user.id):
        await update.message.reply_text(
            f"{E['error']} ඔබව තහනම් කර ඇත!",
            parse_mode='Markdown'
        )
        return
    
    text, keyboard = contact_message()
    
    try:
        await update.message.reply_photo(
            photo=BANNER_CONTACT,
            caption=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stats command handler"""
    user = update.effective_user
    
    # Check if banned
    if await is_user_banned(user.id):
        await update.message.reply_text(
            f"{E['error']} ඔබව තහනම් කර ඇත!",
            parse_mode='Markdown'
        )
        return
    
    try:
        total_users = await db.db.users.count_documents({})
        total_files = await db.db.files.count_documents({})
        total_searches = await db.db.searches.count_documents({})
        banned_users = await db.db.banned_users.count_documents({})
        
        # User stats
        user_data = await db.db.users.find_one({'user_id': user.id})
        user_searches = user_data.get('searches_count', 0) if user_data else 0
        
        text = f"""
╔═══════════════════════════╗
║  📊 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦  ║
╚═══════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 **පද්ධතිය:**
━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 මුළු Users: **{total_users:,}**
📁 මුළු Files: **{total_files:,}**
🔍 මුළු Searches: **{total_searches:,}**
{E['error']} Banned Users: **{banned_users}**

━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 **ඔබේ Stats:**
━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 ඔබේ Searches: **{user_searches}**
"""
        
        if user.id in ADMIN_IDS:
            text += f"\n{E['admin']} **Admin Status: Active**"
        
        text += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        keyboard = [[InlineKeyboardButton(f"{E['back']} ආපසු", callback_data="start")]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in stats: {e}")
        await update.message.reply_text(
            f"{E['error']} දෝෂයක් සිදුවිය!\n\nකරුණාකර නැවත උත්සාහ කරන්න."
        )

# ============================================
# BAN/UNBAN COMMANDS
# ============================================

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban user command"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} Admin only command!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            f"{E['warning']} **Usage:**\n\n"
            f"/ban <user_id or @username> [reason]\n\n"
            f"**Examples:**\n"
            f"/ban 123456789 Spam\n"
            f"/ban @username Abuse",
            parse_mode='Markdown'
        )
        return
    
    target = context.args[0]
    reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
    
    # Check if target is user_id or username
    try:
        if target.startswith('@'):
            # Search by username
            username = target[1:]
            user_data = await db.db.users.find_one({'username': username})
            if not user_data:
                await update.message.reply_text(f"{E['error']} User not found!")
                return
            target_id = user_data['user_id']
        else:
            target_id = int(target)
        
        # Ban user
        success = await ban_user(target_id, user.id, reason)
        
        if success:
            await update.message.reply_text(
                f"{E['success']} **User Banned!**\n\n"
                f"User ID: `{target_id}`\n"
                f"Reason: {reason}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"{E['error']} Failed to ban user!")
            
    except ValueError:
        await update.message.reply_text(f"{E['error']} Invalid user ID!")
    except Exception as e:
        logger.error(f"Error in ban command: {e}")
        await update.message.reply_text(f"{E['error']} Error: {e}")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban user command"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} Admin only command!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            f"{E['warning']} **Usage:**\n\n"
            f"/unban <user_id or @username>\n\n"
            f"**Examples:**\n"
            f"/unban 123456789\n"
            f"/unban @username",
            parse_mode='Markdown'
        )
        return
    
    target = context.args[0]
    
    try:
        if target.startswith('@'):
            # Search by username
            username = target[1:]
            user_data = await db.db.users.find_one({'username': username})
            if not user_data:
                await update.message.reply_text(f"{E['error']} User not found!")
                return
            target_id = user_data['user_id']
        else:
            target_id = int(target)
        
        # Unban user
        success = await unban_user(target_id)
        
        if success:
            await update.message.reply_text(
                f"{E['success']} **User Unbanned!**\n\n"
                f"User ID: `{target_id}`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"{E['warning']} User was not banned or already unbanned!"
            )
            
    except ValueError:
        await update.message.reply_text(f"{E['error']} Invalid user ID!")
    except Exception as e:
        logger.error(f"Error in unban command: {e}")
        await update.message.reply_text(f"{E['error']} Error: {e}")

# ============================================
# MESSAGE HANDLER (SEARCH)
# ============================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages for search"""
    user = update.effective_user
    query = update.message.text.strip()
    
    # Check if banned
    if await is_user_banned(user.id):
        await update.message.reply_text(
            f"{E['error']} ඔබව තහනම් කර ඇත!",
            parse_mode='Markdown'
        )
        return
    
    if not query or len(query) < 2:
        return
    
    await save_user(user)
    
    # Save search query
    await db.db.searches.insert_one({
        'user_id': user.id,
        'query': query,
        'timestamp': datetime.now()
    })
    
    # Update user search count
    await db.db.users.update_one(
        {'user_id': user.id},
        {'$inc': {'searches_count': 1}}
    )
    
    # Search files
    try:
        search_results = await db.db.files.find(
            {'$text': {'$search': query}}
        ).limit(50).to_list(50)
        
        if not search_results:
            # Try regex search as fallback
            search_results = await db.db.files.find({
                '$or': [
                    {'file_name': {'$regex': query, '$options': 'i'}},
                    {'caption': {'$regex': query, '$options': 'i'}}
                ]
            }).limit(50).to_list(50)
        
        if not search_results:
            await update.message.reply_text(
                f"{E['search']} **සෙවුම: \"{query}\"**\n\n"
                f"{E['error']} ප්‍රතිඵල හමු නොවීය!\n\n"
                f"💡 **උපදෙස්:**\n"
                f"• වෙනත් නමකින් උත්සාහ කරන්න\n"
                f"• Spelling පරීක්ෂා කරන්න\n"
                f"• /request භාවිතයෙන් ඉල්ලීමක් කරන්න",
                parse_mode='Markdown'
            )
            return
        
        # Store results in context for pagination
        context.user_data['search_results'] = search_results
        context.user_data['search_query'] = query
        context.user_data['current_page'] = 0
        
        # Send first page
        await send_search_results_page(update, context, 0)
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        await update.message.reply_text(
            f"{E['error']} සෙවීමේදී දෝෂයක්!\n\nකරුණාකර නැවත උත්සාහ කරන්න."
        )

async def send_search_results_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    """Send paginated search results"""
    results = context.user_data.get('search_results', [])
    query = context.user_data.get('search_query', '')
    
    if not results:
        return
    
    # Pagination
    per_page = 10
    total_pages = (len(results) + per_page - 1) // per_page
    page = max(0, min(page, total_pages - 1))
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_results = results[start_idx:end_idx]
    
    # Create result message
    text = f"""
{E['search']} **සෙවුම්: \"{query}\"**

{E['success']} **ප්‍රතිඵල: {len(results)}**
📄 පිටුව {page + 1}/{total_pages}

━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Create buttons
    keyboard = []
    for idx, file_data in enumerate(page_results):
        file_name = file_data['file_name']
        file_size = format_file_size(file_data.get('file_size', 0))
        
        # Truncate long names
        display_name = file_name if len(file_name) <= 50 else file_name[:47] + "..."
        
        button_text = f"📁 {display_name} ({file_size})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"file_{file_data['file_id']}")])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(f"{E['back']} Previous", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(f"Next ➡️", callback_data=f"page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(f"{E['home']} මුල් පිටුව", callback_data="start")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send or edit message
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            await update.callback_query.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# ============================================
# BUTTON CALLBACK HANDLER
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    data = query.data
    
    # Check if banned
    if await is_user_banned(user.id):
        await query.message.reply_text(
            f"{E['error']} ඔබව තහනම් කර ඇත!",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Handle different callback types
        if data == "start":
            text, keyboard = welcome_message(user.first_name)
            try:
                await query.message.delete()
                await query.message.reply_photo(
                    photo=BANNER_START,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            except:
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
        
        elif data == "help":
            text, keyboard = help_message()
            try:
                await query.message.delete()
                await query.message.reply_photo(
                    photo=BANNER_HELP,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            except:
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
        
        elif data == "contact":
            text, keyboard = contact_message()
            try:
                await query.message.delete()
                await query.message.reply_photo(
                    photo=BANNER_CONTACT,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            except:
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
        
        elif data == "search":
            text = f"""
{E['search']} **සෙවීම**

Movie හෝ Series නම ටයිප් කරන්න...

උදා:
• Avatar
• Money Heist
• Spiderman 2021
"""
            keyboard = [[InlineKeyboardButton(f"{E['back']} ආපසු", callback_data="start")]]
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        elif data == "request":
            await request_start(update, context)
        
        elif data.startswith("page_"):
            page = int(data.split("_")[1])
            context.user_data['current_page'] = page
            await send_search_results_page(update, context, page)
        
        elif data.startswith("file_"):
            file_id = data.replace("file_", "")
            await send_file(update, context, file_id)
        
        elif data.startswith("approve_"):
            await handle_request_approval(update, context, True)
        
        elif data.startswith("reject_"):
            await handle_request_approval(update, context, False)
        
        elif data == "broadcast_send":
            await broadcast_confirm_send(update, context)
        
        elif data == "broadcast_cancel":
            await query.edit_message_text(
                f"{E['error']} Broadcast cancelled!",
                parse_mode='Markdown'
            )
            context.user_data.clear()
    
    except Exception as e:
        logger.error(f"Error in button callback: {e}")
        try:
            await query.message.reply_text(
                f"{E['error']} දෝෂයක් සිදුවිය!\n\nකරුණාකර නැවත උත්සාහ කරන්න."
            )
        except:
            pass

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str):
    """Send file to user with beautiful caption"""
    query = update.callback_query
    
    try:
        # Get file from database
        file_data = await db.db.files.find_one({'file_id': file_id})
        
        if not file_data:
            await query.answer(f"{E['error']} File not found!", show_alert=True)
            return
        
        # Create beautiful caption
        caption = create_file_caption(file_data['file_name'], file_data.get('file_size', 0))
        
        # Send file
        await query.answer(f"{E['loading']} Sending file...")
        
        file_type = file_data['file_type']
        
        if file_type == 'document':
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file_id,
                caption=caption,
                parse_mode='Markdown'
            )
        elif file_type == 'video':
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=file_id,
                caption=caption,
                parse_mode='Markdown'
            )
        elif file_type == 'audio':
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=file_id,
                caption=caption,
                parse_mode='Markdown'
            )
        elif file_type == 'photo':
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=file_id,
                caption=caption,
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await query.answer(f"{E['error']} Error sending file!", show_alert=True)

# ============================================
# REQUEST SYSTEM
# ============================================

async def request_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start request conversation"""
    user = update.effective_user
    
    # Check if banned
    if await is_user_banned(user.id):
        if update.callback_query:
            await update.callback_query.answer(
                f"{E['error']} ඔබව තහනම් කර ඇත!",
                show_alert=True
            )
        else:
            await update.message.reply_text(
                f"{E['error']} ඔබව තහනම් කර ඇත!",
                parse_mode='Markdown'
            )
        return ConversationHandler.END
    
    text = f"""
{E['request']} **ඉල්ලීම් පද්ධතිය**

━━━━━━━━━━━━━━━━━━━━━━━━━━

කරුණාකර Movie හෝ Series **නම** එවන්න:

උදා: *Avatar*, *Money Heist*

━━━━━━━━━━━━━━━━━━━━━━━━━

/cancel - අවලංගු කරන්න
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode='Markdown'
        )
    
    return AWAITING_REQUEST_NAME

async def request_receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive request name"""
    context.user_data['request_name'] = update.message.text
    
    text = f"""
{E['request']} **නම:** {update.message.text}

━━━━━━━━━━━━━━━━━━━━━━━━━━

දැන් **වසර** එවන්න:

උදා: *2021*, *2022*

━━━━━━━━━━━━━━━━━━━━━━━━━

/cancel - අවලංගු කරන්න
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')
    return AWAITING_REQUEST_YEAR

async def request_receive_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive request year and save"""
    user = update.effective_user
    year = update.message.text
    name = context.user_data.get('request_name', 'Unknown')
    
    # Save request
    request_doc = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'request_name': name,
        'request_year': year,
        'status': 'pending',
        'created_at': datetime.now()
    }
    
    result = await db.db.requests.insert_one(request_doc)
    
    # Send to admin channel if set
    if REQUEST_CHANNEL_ID:
        try:
            admin_text = f"""
{E['new']} **නව ඉල්ලීමක්!**

━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 **User:** {user.first_name} (@{user.username})
🆔 **User ID:** `{user.id}`

📝 **නම:** {name}
📅 **වසර:** {year}

━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            keyboard = [
                [
                    InlineKeyboardButton(f"{E['success']} Approve", callback_data=f"approve_{result.inserted_id}"),
                    InlineKeyboardButton(f"{E['error']} Reject", callback_data=f"reject_{result.inserted_id}")
                ]
            ]
            
            await context.bot.send_message(
                chat_id=REQUEST_CHANNEL_ID,
                text=admin_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending to admin channel: {e}")
    
    # Confirm to user
    await update.message.reply_text(
        f"{E['success']} **ඉල්ලීම සාර්ථකයි!**\n\n"
        f"📝 නම: {name}\n"
        f"📅 වසර: {year}\n\n"
        f"Admin අනුමැතියෙන් පසු ඔබට දැනුම් දෙනු ලැබේ.\n\n"
        f"{E['fire']} ස්තූතියි!",
        parse_mode='Markdown'
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def request_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel request conversation"""
    await update.message.reply_text(
        f"{E['error']} අවලංගු කරන ලදි!",
        parse_mode='Markdown'
    )
    context.user_data.clear()
    return ConversationHandler.END

async def handle_request_approval(update: Update, context: ContextTypes.DEFAULT_TYPE, approved: bool):
    """Handle request approval/rejection"""
    query = update.callback_query
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await query.answer("Admin only!", show_alert=True)
        return
    
    try:
        from bson.objectid import ObjectId
        request_id = query.data.split("_")[1]
        
        # Get request
        request_data = await db.db.requests.find_one({'_id': ObjectId(request_id)})
        
        if not request_data:
            await query.answer("Request not found!", show_alert=True)
            return
        
        # Update status
        status = 'approved' if approved else 'rejected'
        await db.db.requests.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': {'status': status, 'reviewed_at': datetime.now(), 'reviewed_by': user.id}}
        )
        
        # Notify user
        user_id = request_data['user_id']
        name = request_data['request_name']
        year = request_data['request_year']
        
        if approved:
            user_msg = f"""
{E['success']} **ඉල්ලීම අනුමත විය!**

━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 නම: {name}
📅 වසර: {year}

අපි ඉක්මනින් file එක එකතු කරන්නෙමු.
ස්තූතියි!
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            user_msg = f"""
{E['error']} **ඉල්ලීම ප්‍රතික්ෂේප විය**

━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 නම: {name}
📅 වසර: {year}

කණගාටුයි, මෙම file එක දැනට ලබා ගත නොහැක.
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=user_msg,
                parse_mode='Markdown'
            )
        except:
            pass
        
        # Update admin message
        status_text = f"{E['success']} APPROVED" if approved else f"{E['error']} REJECTED"
        await query.edit_message_text(
            f"{query.message.text}\n\n{status_text} by @{user.username}",
            parse_mode='Markdown'
        )
        
        await query.answer(f"Request {status}!", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error handling request approval: {e}")
        await query.answer("Error!", show_alert=True)

# ============================================
# ADMIN COMMANDS
# ============================================

async def delete_duplicates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete duplicate files (admin only)"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} Admin only!")
        return
    
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
            f"{E['success']} **Deleted {deleted_count} duplicate files!**\n"
            f"Found {len(duplicates)} duplicate groups.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error deleting duplicates: {e}")
        await update.message.reply_text(f"{E['error']} Error: {e}")

# ============================================
# BROADCAST SYSTEM WITH CONFIRMATION
# ============================================

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text(f"{E['error']} No permission!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        f"📢 **Broadcast Message**\n\n"
        f"Send me the message to broadcast:\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ You can send text\n"
        f"✅ You can send photo with caption\n"
        f"✅ You can send video with caption\n"
        f"✅ You can forward a message\n"
        f"✅ Buttons will be preserved\n\n"
        f"/cancel to cancel",
        parse_mode='Markdown'
    )
    
    return AWAITING_BROADCAST_MESSAGE

async def broadcast_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive broadcast message and ask for confirmation"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        return ConversationHandler.END
    
    # Store message for broadcasting
    context.user_data['broadcast_message'] = update.message
    
    # Count users
    users_count = await db.db.users.count_documents({})
    
    # Ask for confirmation
    keyboard = [
        [
            InlineKeyboardButton(f"{E['success']} Send", callback_data="broadcast_send"),
            InlineKeyboardButton(f"{E['error']} Cancel", callback_data="broadcast_cancel")
        ]
    ]
    
    await update.message.reply_text(
        f"📢 **Broadcast Confirmation**\n\n"
        f"Ready to broadcast to **{users_count}** users.\n\n"
        f"Send this message?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return AWAITING_BROADCAST_CONFIRM

async def broadcast_confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and send broadcast"""
    query = update.callback_query
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await query.answer("No permission!", show_alert=True)
        return ConversationHandler.END
    
    await query.answer()
    
    users = await db.db.users.find({}).to_list(None)
    
    await query.edit_message_text(
        f"📢 Broadcasting to **{len(users)}** users...\n"
        f"{E['loading']} This may take a few minutes.",
        parse_mode='Markdown'
    )
    
    sent = 0
    failed = 0
    message_to_broadcast = context.user_data['broadcast_message']
    
    for user_data in users:
        try:
            # Copy message to preserve all content, buttons, media
            await message_to_broadcast.copy(chat_id=user_data['user_id'])
            sent += 1
        except Exception as e:
            failed += 1
            logger.debug(f"Failed to send to {user_data['user_id']}: {e}")
    
    await query.message.reply_text(
        f"{E['success']} **Broadcast Complete!**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Sent: **{sent}**\n"
        f"❌ Failed: **{failed}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
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
                f"{E['error']} **දෝෂයක් සිදුවිය!**\n\n"
                f"කරුණාකර නැවත උත්සාහ කරන්න හෝ /contact භාවිතා කරන්න.",
                parse_mode='Markdown'
            )
        except:
            pass

# ============================================
# INITIALIZATION
# ============================================

async def post_init(app: Application):
    """Initialize bot"""
    logger.info("🚀 Starting Sinhala Subtitle Bot...")
    
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
        ("ban", "Ban user (Admin)"),
        ("unban", "Unban user (Admin)"),
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
            AWAITING_BROADCAST_MESSAGE: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_receive)],
            AWAITING_BROADCAST_CONFIRM: []  # Handled by callback
        },
        fallbacks=[CommandHandler('cancel', request_cancel)]
    )
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("deleteduplicates", delete_duplicates))
    app.add_handler(request_conv)
    app.add_handler(broadcast_conv)
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, channel_post_handler))
    app.add_error_handler(error_handler)
    
    # Run bot
    logger.info("🤖 Sinhala Subtitle Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
