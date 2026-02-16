# 🎬 SINHALA SUBTITLE BOT - ULTRA PRO V2 ENHANCED

සිංහල උපසිරැසි බොට් - සම්පූර්ණ ක්‍රියාකාරී Telegram bot එකක්

## ✨ Enhanced Features (V2)

### 🆕 New in This Version:
- ✅ **Beautiful File Captions** - Formatted title, year, size with custom styling
- ✅ **NO Force Subscription** - Free access for all users
- ✅ **Ban/Unban System** - Admin can ban/unban users by ID or username
- ✅ **Broadcast with Confirmation** - Send/Cancel buttons before broadcasting
- ✅ **Forward Message Support** - Preserve images, buttons, and formatting in broadcasts
- ✅ **Fixed Pagination** - Working Next/Back buttons for search results
- ✅ **Menu Banners** - Beautiful images on all menu screens
- ✅ **Enhanced Emojis** - Beautiful formatting throughout
- ✅ **Better Error Handling** - All commands work properly

### 📚 Core Features:
- 🔍 **Advanced Search** - Full-text and regex search
- 📁 **Auto File Indexing** - Files from channel automatically indexed
- 📝 **Request System** - Users can request movies/series
- 📊 **Statistics** - Track users, files, searches
- 👑 **Admin Panel** - Ban/unban, broadcast, delete duplicates
- 💾 **Smart Storage** - MongoDB with duplicate detection
- 🎨 **Beautiful UI** - Emojis and formatted messages

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB database
- Telegram Bot Token

### Installation

1. **Clone/Download**
```bash
unzip sinhala-sub-bot-v2-complete.zip
cd sinhala-sub-bot-v2-complete
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt --break-system-packages
```

3. **Configure Environment**
Create `.env` file:
```env
BOT_TOKEN=your_bot_token_here
MONGODB_URI=your_mongodb_uri_here
DB_NAME=sinhala_sub_bot
ADMIN_IDS=123456789,987654321
CHANNEL_ID=-1001234567890
CHANNEL_USERNAME=@YourChannel
REQUEST_CHANNEL_ID=-1001234567890
BOT_USERNAME=YourBotUsername

# Contact Information
DEVELOPER_NAME=Sadesha Hansana
OWNER_NAME=Sadisa Harshana
DEVELOPER_LINK=https://t.me/YourDeveloper
OWNER_LINK=https://t.me/YourOwner
OWNER_WHATSAPP=https://wa.me/94701234567

# Menu Banner Images (Telegraph or Telegram file_id)
BANNER_START=https://telegra.ph/file/yourimage1.jpg
BANNER_HELP=https://telegra.ph/file/yourimage2.jpg
BANNER_CONTACT=https://telegra.ph/file/yourimage3.jpg
BANNER_SEARCH=https://telegra.ph/file/yourimage4.jpg
```

4. **Run Bot**
```bash
python bot.py
```

## 📖 Commands

### User Commands:
- `/start` - Start bot and show main menu
- `/help` - Show help and usage guide
- `/search` - Search for movies/series
- `/request` - Request a movie/series
- `/contact` - Contact developers/owner
- `/stats` - View bot statistics

### Admin Commands:
- `/ban <user_id or @username> [reason]` - Ban a user
- `/unban <user_id or @username>` - Unban a user
- `/broadcast` - Broadcast message to all users
- `/deleteduplicates` - Remove duplicate files

## 🎯 How It Works

### For Users:

1. **Search Files:**
   - Type movie/series name
   - Click on result button
   - Download file with beautiful caption

2. **Request Files:**
   - Use `/request` command
   - Enter name and year
   - Wait for admin approval

3. **Contact Support:**
   - Use `/contact` command
   - Click on Developer/Owner buttons
   - Direct WhatsApp link available

### For Admins:

1. **Ban/Unban Users:**
   ```
   /ban 123456789 Spamming
   /ban @username Abuse
   /unban 123456789
   /unban @username
   ```

2. **Broadcast Messages:**
   - Use `/broadcast` command
   - Send any message (text/photo/video/forward)
   - Confirm with Send button
   - All formatting and buttons preserved

3. **Manage Files:**
   - Add bot as admin to your channel
   - Files are auto-indexed
   - Remove duplicates with `/deleteduplicates`

## 📁 File Caption Format

When users download files, they receive this beautiful caption:

```
📁𝗧𝗶𝘁𝗹𝗲  - Avatar The Way of Water
🔎𝗬𝗲𝗮𝗿  - 2022
💾𝗦𝗶𝘇𝗲   - 2.45 GB

𝗦𝗜𝗡𝗛𝗔𝗟𝗔  𝗦𝗨𝗕𝗧𝗜𝗧𝗟𝗘  𝗕𝗢𝗧
🧑‍💻𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐝 𝐁𝐲 - 𝗦𝗮𝗱𝗲𝘀𝗵𝗮 𝗛𝗮𝗻𝘀𝗮𝗻𝗮
🙎‍♂️𝐏𝐫𝐨𝐝𝐮𝐬𝐞 𝐀𝐧𝐝 𝐎𝐰𝐧𝐞𝐫 - 𝗦𝗮𝗱𝗶𝘀𝗮 𝗛𝗮𝗿𝘀𝗵𝗮𝗻𝗮
```

## 🎨 Menu Banners

All menus display beautiful banner images:
- Start Menu - Welcome banner
- Help Menu - Help banner
- Contact Menu - Contact banner
- Search Results - Search banner

Upload images to Telegraph or use Telegram file_id in `.env`

## 🔧 Configuration Tips

### Getting Channel ID:
1. Forward message from channel to @userinfobot
2. Copy the channel ID (starts with -100)

### Getting Bot Token:
1. Talk to @BotFather
2. Create new bot
3. Copy the token

### MongoDB Setup:
1. Create free account at MongoDB Atlas
2. Create cluster
3. Get connection URI
4. Add to `.env` file

### Admin IDs:
1. Get your Telegram ID from @userinfobot
2. Add comma-separated IDs to ADMIN_IDS

## 📱 Bot Features in Detail

### 1. Search System
- Full-text search
- Regex fallback search
- Pagination (10 results per page)
- Working Next/Back buttons
- File size display
- Quick download buttons

### 2. Ban System
- Ban by user ID: `/ban 123456789 Spam`
- Ban by username: `/ban @baduser Abuse`
- Unban by ID or username
- Banned users cannot use bot
- MongoDB tracking

### 3. Broadcast System
- Send text messages
- Send photos with captions
- Send videos with captions
- Forward any message
- Buttons preserved
- Confirmation before sending
- Progress tracking

### 4. Request System
- Two-step process (name → year)
- Saved to database
- Sent to admin channel
- Approve/Reject buttons
- User notification

### 5. File Management
- Auto-indexing from channel
- Duplicate detection
- Multiple file types (video, document, audio, photo)
- Beautiful captions
- Size formatting

## 🐛 Bug Fixes

All previous issues fixed:
- ✅ File captions formatted perfectly
- ✅ Channel subscription removed
- ✅ Ban/unban working with ID and username
- ✅ Broadcast confirmation added
- ✅ Forward messages preserved
- ✅ Pagination buttons working
- ✅ Contact command working
- ✅ Help command working
- ✅ Error handler improved
- ✅ All menus show images

## 🌐 Deployment

### Deploy to Heroku:
```bash
heroku create your-bot-name
heroku config:set BOT_TOKEN=your_token
heroku config:set MONGODB_URI=your_uri
git push heroku main
```

### Deploy to Railway:
1. Connect GitHub repository
2. Add environment variables
3. Deploy

### Deploy to VPS:
```bash
python3 bot.py
# Or use screen/tmux
screen -S sinhalasub
python3 bot.py
# Detach: Ctrl+A, D
```

## 📞 Support

### Developer:
- 🧑‍💻 Sadesha Hansana
- Telegram: [Link in bot]

### Owner:
- 🙎‍♂️ Sadisa Harshana
- Telegram: [Link in bot]
- WhatsApp: [Link in bot]

## 📄 License

This project is for personal/educational use.

## 🔄 Updates

### Version 2.0 (Current)
- Beautiful file captions
- No force subscription
- Ban/unban system
- Broadcast confirmation
- Fixed pagination
- Menu banners
- Enhanced UI

### Version 1.0
- Basic search
- File indexing
- Request system
- Admin commands

## 🎯 Future Plans

- Multi-language support
- Advanced filters
- Download statistics
- User favorites
- Rating system
- Category browsing

## ⚠️ Important Notes

1. Bot must be admin in your channel for auto-indexing
2. MongoDB URI must be valid and accessible
3. Admin IDs must be correct (no spaces)
4. Channel ID includes the -100 prefix
5. Banner images optional but recommended
6. Use Telegraph for image hosting

## 🙏 Credits

Developed with ❤️ for Sinhala subtitle community

---

**Enjoy your enhanced Sinhala Subtitle Bot!** 🎬🇱🇰
