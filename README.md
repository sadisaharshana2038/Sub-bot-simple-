# 🎬 Sinhala Subtitle Bot - Ultra Pro V2

සිංහල උපසිරැසි බොට් - සම්පූර්ණ ක්‍රියාකාරී bot එකක්

## 🆕 New Features

### ✅ File Indexing System
- Channel එකට යන **ඕනම file එකක්** auto index වෙනවා
- Documents, Videos, Audio, Photos - සියල්ල support කරනවා
- SRT, ZIP, RAR, MP4, MKV - ඕනම format එකක්

### ✅ Bot Mention Reply
- Bot නම mention කළම search වෙනවා
- Example: `@YourBot breaking bad`

### ✅ Contact System
- `/contact` command එකෙන් contact info එනවා
- Developer, Owner, WhatsApp links සමග buttons
- Custom message එකක් දාන්න පුළුවන්

### ✅ Request System
- `/request` command එකෙන් film request කරන්න පුළුවන්
- Film name හා year එකත් ඉල්ලනවා
- Admin channel එකට යනවා Done/Reject buttons සමග
- User ට auto reply එනවා admin response එකට

### ✅ Enhanced Statistics
- Live updating stats
- Total users, Monthly active users
- Channels, Groups count
- Total searches, Indexed files
- ලස්සන formatting එක්ක

### ✅ Duplicate File Removal
- `/deleteduplicates` command
- Auto detect කරලා duplicates delete කරනවා

### ✅ Advanced Broadcast
- Text, Photos, Videos, Documents - ඕනම එකක් යවන්න පුළුවන්
- Forward messages - එකත් work කරනවා
- Buttons preserve වෙනවා
- Success/Failure count එනවා

### ✅ Pagination
- 10 results බැගින් results එනවා
- Previous/Next buttons
- ලස්සන navigation

### ✅ Clean Start Menu
- Featured, Trending buttons අයින් කළා
- Clean හා simple interface එකක්

## 📋 Requirements

```
python-telegram-bot>=20.0
motor>=3.0
python-dotenv
```

## 🔧 Setup Instructions

### 1. MongoDB Setup

```bash
# Install MongoDB or use MongoDB Atlas (cloud)
# Get your MongoDB URI
```

### 2. Environment Variables

Create `.env` file:

```env
# Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=YourBotUsername

# MongoDB
MONGODB_URI=mongodb://localhost:27017
DB_NAME=sinhala_sub_bot

# Admins (comma separated user IDs)
ADMIN_IDS=123456789,987654321

# Main Channel (for file indexing)
CHANNEL_ID=-1001234567890
CHANNEL_USERNAME=@YourChannel
FORCE_SUBSCRIBE=true

# Request System (Admin channel for requests)
REQUEST_CHANNEL_ID=-1001234567890

# Contact Information
DEVELOPER_LINK=https://t.me/YourDeveloper
OWNER_LINK=https://t.me/YourOwner
OWNER_WHATSAPP=https://wa.me/94701234567
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Bot

```bash
python bot.py
```

## 🤖 Bot Setup

### 1. Create Bot
- Talk to [@BotFather](https://t.me/BotFather)
- Create new bot: `/newbot`
- Get your bot token
- Set bot username: `/setusername`

### 2. Add Bot to Channel
- Add bot as **administrator** to your channel
- Bot needs **all permissions** to index files
- Get channel ID (use [@userinfobot](https://t.me/userinfobot))

### 3. Admin Channel for Requests
- Create a private channel for admin team
- Add bot as administrator
- Get channel ID
- Set as `REQUEST_CHANNEL_ID`

### 4. Get Your User ID
- Talk to [@userinfobot](https://t.me/userinfobot)
- Add your ID to `ADMIN_IDS`

## 📚 Usage

### User Commands
- `/start` - ආරම්භ කරන්න
- `/help` - උදව්
- `/search` - සෙවීම
- `/request` - Film request කරන්න
- `/contact` - සම්බන්ධ වන්න
- `/stats` - Statistics

### Admin Commands
- `/broadcast` - Message යවන්න (all users)
- `/deleteduplicates` - Duplicate files ඉවත් කරන්න
- `/indexstats` - Indexing statistics

### Searching
- Type film name දුන්නම search වෙනවා
- Bot mention කළත් work කරනවා: `@YourBot film name`
- 10 results බැගින් pagination

## 🗃️ Database Collections

### users
```json
{
  "user_id": 123456789,
  "username": "user123",
  "first_name": "John",
  "joined_date": "2024-01-01",
  "searches_count": 50,
  "is_admin": false
}
```

### files
```json
{
  "file_id": "BAACAgIAAxkBAAI...",
  "file_unique_id": "AgADxxxx",
  "file_name": "Breaking.Bad.S01E01.srt",
  "file_type": "document",
  "file_size": 50000,
  "caption": "Breaking Bad Season 1 Episode 1",
  "message_id": 123,
  "chat_id": -1001234567890,
  "indexed_date": "2024-01-01"
}
```

### requests
```json
{
  "user_id": 123456789,
  "username": "user123",
  "film_name": "Breaking Bad",
  "year": "2008-2013",
  "status": "pending",
  "request_date": "2024-01-01"
}
```

### searches
```json
{
  "user_id": 123456789,
  "query": "breaking bad",
  "timestamp": "2024-01-01"
}
```

### chats
```json
{
  "chat_id": -1001234567890,
  "title": "My Channel",
  "username": "mychannel",
  "type": "channel",
  "last_updated": "2024-01-01"
}
```

## 🔥 Features Explained

### File Indexing
Bot automatically indexes **every file** posted to your channel:
- Documents (.srt, .zip, .rar, .pdf, etc.)
- Videos (.mp4, .mkv, .avi, etc.)
- Audio files
- Photos

Files are searchable by:
- File name
- Caption text

### Search System
- Users can search by typing any text
- Bot mention also works: `@YourBot search term`
- Results show 10 per page
- Previous/Next navigation
- Click file button to download

### Request System
1. User sends `/request`
2. Bot asks for film name (English)
3. Bot asks for year
4. Request goes to admin channel with Done/Reject buttons
5. Admin clicks Done or Reject
6. User gets automatic notification

### Contact System
- Shows custom contact message
- Developer, Owner, WhatsApp buttons
- Fully customizable via .env

### Stats Display
- Real-time stats
- User counts (total, monthly active)
- Chat counts (channels, groups)
- Search count
- Indexed files count
- Beautiful formatting

### Broadcast System
- Supports text, photos, videos, documents
- Forward messages work
- Buttons are preserved
- Shows success/failure count
- Works for all users in database

### Duplicate Removal
- Finds files with same `file_unique_id`
- Keeps first, deletes rest
- Shows count of deleted files

## 🛠️ Troubleshooting

### Bot not indexing files?
1. Check bot is admin in channel
2. Check `CHANNEL_ID` is correct (with `-100` prefix)
3. Check bot has all permissions

### Search not working?
1. Check MongoDB connection
2. Check files are indexed: `/stats`
3. Try exact file name first

### Broadcast not sending?
1. Check users are in database
2. Some users may have blocked bot
3. Check for error logs

### Request system not working?
1. Check `REQUEST_CHANNEL_ID` is set
2. Bot must be admin in that channel
3. Check admin user IDs in `ADMIN_IDS`

## 📝 Notes

- Bot name mention feature needs `BOT_USERNAME` in .env
- Request channel can be same as main channel
- Multiple admins can be added (comma separated IDs)
- Files are never duplicated in database (unique file_unique_id)
- Stats update in real-time
- Bot works with any file type Telegram supports

## 🎯 Best Practices

1. **Backup Database** regularly
2. **Monitor Bot** with `/stats`
3. **Clean Duplicates** periodically with `/deleteduplicates`
4. **Test Features** in test group first
5. **Keep Logs** for debugging

## 📞 Support

Bot ගැන ප්‍රශ්න තියෙනවනම්:
- Developer link use කරන්න
- Owner contact කරන්න
- `/contact` command use කරන්න

## 🔐 Security

- Never share your `.env` file
- Keep bot token secure
- Only trusted users as admins
- Regular database backups
- Monitor bot logs

## 📄 License

This bot is for personal/educational use.

---

🇱🇰 Made with ❤️ for Sinhala subtitle community
