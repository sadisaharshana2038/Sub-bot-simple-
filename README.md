# 🎬 Sinhala Subtitle Bot - Simple Version

සරල, සම්පූර්ණ Telegram bot එකක් - පහසුවෙන් deploy කරන්න!

## ✨ විශේෂාංග / Features

- ✅ සිංහල/English support
- ✅ Series & Episode management
- ✅ Smart search
- ✅ Download tracking
- ✅ User statistics
- ✅ Admin panel
- ✅ Broadcast system

## 📁 Files (එච්චර files නෑ!)

```
sinhala-sub-bot-simple/
├── bot.py              # Main bot (all logic here!)
├── admin.py            # Admin functions
├── setup.py            # Database setup
├── requirements.txt    # Dependencies
├── .env.example        # Configuration template
└── README.md           # This file
```

## 🚀 Quick Start (5 minutes!)

### 1️⃣ Bot Token එක ගන්න

1. Telegram open කරන්න
2. `@BotFather` search කරන්න
3. `/newbot` send කරන්න
4. Bot name හා username දෙන්න
5. **Token එක save කරන්න**

### 2️⃣ MongoDB Setup කරන්න

1. [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) යන්න
2. Free account එකක් හදන්න
3. Free cluster (M0) එකක් create කරන්න
4. Database user එකක් add කරන්න (username & password)
5. Network Access → IP Whitelist → `0.0.0.0/0` add කරන්න
6. **Connection string එක copy කරන්න**

### 3️⃣ Bot Configure කරන්න

1. `.env.example` file එක copy කරලා `.env` කියලා rename කරන්න

2. `.env` file එක edit කරන්න:

```env
BOT_TOKEN=your_bot_token_from_botfather
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
ADMIN_IDS=your_telegram_id
```

**ඔබගේ Telegram ID එක හොයන්න:**
- Telegram එකේ `@userinfobot` එකට message කරන්න
- එයා reply කරන ID එක copy කරන්න

### 4️⃣ Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python setup.py

# Run bot
python bot.py
```

**හරි! Bot එක දැන් run වෙනවා!** 🎉

Telegram එකේ bot එකට `/start` කරලා test කරන්න

## 📸 Image Links Setup කරන්න

Bot එකේ images Telegram links වලින් දාන්න ඕන. මෙහෙම කරන්න:

### Method 1: Telegram File ID (Best!)

1. Bot එකටම image එකක් send කරන්න
2. `/getfileid` command එකක් add කරන්න:

```python
async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text(f"File ID: `{file_id}`", parse_mode='Markdown')
```

3. Image එක send කරලා file_id එක copy කරන්න
4. `bot.py` එකේ `IMAGES` dict එකේ update කරන්න:

```python
IMAGES = {
    'welcome': 'AgACAgIAAxkBAAIBY2...',  # Your file_id here
    'loading': 'AgACAgIAAxkBAAIBY3...',
    # ...
}
```

### Method 2: Telegraph (Public URLs)

1. [telegra.ph](https://telegra.ph) යන්න
2. Image upload කරන්න
3. URL එක copy කරන්න (`https://telegra.ph/file/xyz.jpg`)
4. `bot.py` එකේ update කරන්න:

```python
IMAGES = {
    'welcome': 'https://telegra.ph/file/abc123.jpg',
    'loading': 'https://telegra.ph/file/def456.gif',
    # ...
}
```

## 📝 Content Add කරන්න

### Series Add කරන්න

```bash
# Bot එකේ
/addseries

# පස්සේ මේ format එකෙන් send කරන්න:
series_id: breaking_bad
title_en: Breaking Bad
title_si: බ්‍රේකින් බෑඩ්
description_en: A chemistry teacher turns to crime
description_si: රසායන ගුරුවරයෙක් අපරාධ ලෝකයට
category: Drama
rating: 9.5
poster_url: https://telegra.ph/file/poster.jpg
```

### Episode Add කරන්න

```bash
/addepisode

# Format:
episode_id: bb_s01e01
series_id: breaking_bad
season: 1
episode: 1
title: Pilot
file_id: BAACAgIAAxkBAAI...
```

**File ID එක ගන්නේ කොහොමද?**

1. Subtitle file එක bot එකට send කරන්න (document ලෙස)
2. Bot එකේ file එකෙ file_id එක log වෙනවා
3. හෝ `/getfileid` command use කරන්න

## 👑 Admin Commands

```
/admin          - Admin panel
/addseries      - Add new series
/addepisode     - Add new episode
/broadcast      - Send message to all users
/viewstats      - View bot statistics
```

## 👤 User Commands

```
/start          - Start bot
/help           - Get help
/search         - Search series
/browse         - Browse all series
/trending       - Trending series
/stats          - Your statistics
/settings       - Settings
```

## ☁️ Deploy to Heroku (24/7 Free!)

### 1. Heroku Setup

```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-bot-name

# Set config
heroku config:set BOT_TOKEN=your_token
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set ADMIN_IDS=your_id
```

### 2. Create `Procfile`

```
worker: python bot.py
```

### 3. Create `runtime.txt`

```
python-3.11.7
```

### 4. Deploy

```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Scale worker
heroku ps:scale worker=1
```

## 🐛 Troubleshooting

### Bot not responding?

```bash
# Check if running
python bot.py

# Check logs
tail -f bot.log
```

### Database error?

1. Check `.env` file
2. Verify MongoDB connection string
3. Check IP whitelist (0.0.0.0/0)

### Import error?

```bash
pip install -r requirements.txt
```

## 📊 Database Schema

### Users Collection
```json
{
  "user_id": 123456789,
  "username": "john",
  "first_name": "John",
  "language": "si",
  "downloads": 10,
  "searches": 25,
  "points": 50
}
```

### Series Collection
```json
{
  "series_id": "breaking_bad",
  "title_en": "Breaking Bad",
  "title_si": "බ්‍රේකින් බෑඩ්",
  "category": "Drama",
  "rating": 9.5,
  "episodes": 62,
  "is_active": true,
  "is_trending": true
}
```

### Episodes Collection
```json
{
  "episode_id": "bb_s01e01",
  "series_id": "breaking_bad",
  "season": 1,
  "episode": 1,
  "title": "Pilot",
  "file_id": "BAACAgIAAxkBAAI...",
  "downloads": 150
}
```

## 🎯 Tips

1. **Images**: පළමුව Telegram එකට upload කරලා file_id use කරන්න
2. **Testing**: Local එකේ test කරලා පස්සේ deploy කරන්න
3. **Backup**: Database regular backup කරන්න
4. **Monitor**: Logs check කරන්න errors වලට

## 🔐 Security

- `.env` file එක **කවදාවත්** GitHub එකට push කරන්න එපා!
- Bot token එක share කරන්න එපා
- Admin IDs හරියට set කරන්න

## 📞 Support

Issues තිබ්බොත්:
1. GitHub Issues
2. Telegram: @YourSupportBot
3. Email: support@example.com

## 📝 License

MIT License - Free to use!

---

**Made with ❤️ for Sinhala community**

🇱🇰 සිංහල උපසිරැසි බොට්
