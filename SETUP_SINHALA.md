# 🚀 ඉක්මන් Setup Guide

## 1️⃣ Bot Token ගන්න

1. [@BotFather](https://t.me/BotFather) කට message කරන්න
2. `/newbot` command එක යවන්න
3. Bot නමක් දෙන්න
4. Bot username එකක් දෙන්න (@YourBot_bot)
5. Token එක copy කරගන්න

## 2️⃣ MongoDB Setup

### Option A: Local MongoDB
```bash
# Install MongoDB
sudo apt-get install mongodb

# Start MongoDB
sudo systemctl start mongodb
```

### Option B: MongoDB Atlas (Free Cloud)
1. [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) වලට යන්න
2. Free account එකක් හදාගන්න
3. Cluster එකක් create කරන්න
4. Database user එකක් add කරන්න
5. Connection string එක copy කරගන්න

## 3️⃣ Channel Setup

1. Telegram channel එකක් හදාගන්න (public හෝ private)
2. Bot එක channel එකට add කරන්න (**Admin විදියට**)
3. Bot එකට **සියලු permissions** දෙන්න
4. Channel ID එක ගන්න:
   - [@userinfobot](https://t.me/userinfobot) කට channel post එකක් forward කරන්න
   - හෝ [@getidsbot](https://t.me/getidsbot) use කරන්න

## 4️⃣ Admin Channel (Requests සඳහා)

1. Private channel එකක් හදාගන්න admin team එක සඳහා
2. Bot එක add කරන්න (Admin විදියට)
3. Channel ID එක ගන්න

## 5️⃣ .env File හදන්න

`.env` file එකක් create කරන්න:

```env
# Bot Token (BotFather එකෙන් ගත්තේ)
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Bot Username (@ එක නැතුව)
BOT_USERNAME=YourBot

# MongoDB URI
MONGODB_URI=mongodb://localhost:27017
# හෝ Atlas: mongodb+srv://username:password@cluster.mongodb.net

# Database Name
DB_NAME=sinhala_sub_bot

# Admin IDs (ඔබගේ Telegram user ID)
# @userinfobot එකෙන් ගන්න, comma වලින් separate කරන්න
ADMIN_IDS=123456789,987654321

# Channel ID (Main channel - file indexing සඳහා)
CHANNEL_ID=-1001234567890
CHANNEL_USERNAME=@YourChannel

# Force Subscribe (අනිවාර්යයෙන් channel join වෙන්න තියෙන්න)
FORCE_SUBSCRIBE=true

# Admin Channel (Requests යන එක)
REQUEST_CHANNEL_ID=-1001234567890

# Contact Info (ඔබගේ links)
DEVELOPER_LINK=https://t.me/YourDeveloper
OWNER_LINK=https://t.me/YourOwner
OWNER_WHATSAPP=https://wa.me/94701234567
```

## 6️⃣ Dependencies Install කරන්න

```bash
pip install -r requirements.txt
```

## 7️⃣ Bot Run කරන්න

```bash
python bot.py
```

Bot start වෙයි! ✅

## 8️⃣ Test කරන්න

1. Bot එකට `/start` යවන්න
2. Search test කරන්න
3. Channel එකට file එකක් දාන්න (bot auto index කරයි)
4. File එක search කරලා බලන්න
5. `/request` test කරන්න
6. `/contact` test කරන්න
7. `/stats` බලන්න

## 🎯 Important Notes

### Bot Permissions (Channel එකේ)
Bot එකට මේ permissions ඕනෙ:
- ✅ Post messages
- ✅ Edit messages  
- ✅ Delete messages
- ✅ Manage chat
- ✅ View messages

### Admin Commands Test කරන්න
```
/broadcast - Message broadcast එකක් යවන්න test කරන්න
/deleteduplicates - Duplicates check කරන්න
```

### Request System Test කරන්න
1. User විදියට `/request` යවන්න
2. Film name හා year දෙන්න
3. Admin channel එකේ message එක check කරන්න
4. Done/Reject button click කරන්න
5. User එකට message ආවාද බලන්න

## 🐛 Common Issues

### Bot not responding?
- Token එක හරිද check කරන්න
- Bot running ද check කරන්න
- Internet connection check කරන්න

### Files not indexing?
- Bot channel එකේ admin ද check කරන්න
- CHANNEL_ID හරිද check කරන්න (-100 prefix එක්ක)
- Bot එකට permissions තියෙනවද check කරන්න

### Search not working?
- MongoDB connected ද check කරන්න
- Files indexed වෙලා තියෙනවද බලන්න (`/stats`)
- Database name හරිද check කරන්න

### Broadcast not working?
- Admin ද check කරන්න
- Users database එකේ තියෙනවද check කරන්න
- Try small test first

## 📱 Deploy කරන්න (Optional)

### Heroku Deploy
```bash
# Create Heroku app
heroku create your-app-name

# Add buildpack
heroku buildpacks:set heroku/python

# Set config vars (same as .env)
heroku config:set BOT_TOKEN=...
heroku config:set MONGODB_URI=...
# etc...

# Deploy
git push heroku main
```

### VPS Deploy
```bash
# Install Python 3.8+
sudo apt-get install python3 python3-pip

# Clone/upload code
# Install dependencies
pip3 install -r requirements.txt

# Run with screen/tmux
screen -S bot
python3 bot.py
# Ctrl+A then D to detach

# Or use systemd service
```

## ✅ Checklist

- [ ] Bot token ගත්තා
- [ ] MongoDB setup කළා
- [ ] Channel එකක් හැදුවා
- [ ] Bot එක channel එකට add කළා (admin විදියට)
- [ ] Admin channel හැදුවා
- [ ] .env file හැදුවා
- [ ] Dependencies install කළා
- [ ] Bot run කළා
- [ ] /start test කළා
- [ ] File indexing test කළා
- [ ] Search test කළා
- [ ] Request system test කළා
- [ ] Broadcast test කළා

සියල්ල OK නම්, Bot පරිපූර්ණයි! 🎉

---

ප්‍රශ්න තියෙනවනම් README.md file එක කියවන්න හෝ developer contact කරන්න.
