# 🎬 SINHALA SUBTITLE BOT - සම්පූර්ණ Setup මාර්ගෝපදේශය

## 📋 පියවර අනුපියවර Setup කිරීම

### 1️⃣ Bot Token ලබා ගන්නා අයුරු

1. Telegram එකේ @BotFather වෙත යන්න
2. `/newbot` command එක භාවිතා කරන්න
3. Bot නමක් දෙන්න (උදා: Sinhala Sub Bot)
4. Bot username එකක් දෙන්න (උදා: SinhalaSubBot)
5. Token එක copy කරගන්න
6. `.env` file එකට add කරන්න:
   ```
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 2️⃣ MongoDB Database Setup කිරීම

#### Option 1: MongoDB Atlas (නොමිලේ - Recommended)

1. https://www.mongodb.com/cloud/atlas වෙත යන්න
2. "Try Free" click කරන්න
3. Google/Email භාවිතයෙන් account එකක් හදාගන්න
4. Free M0 Cluster එකක් create කරන්න
5. Database User එකක් හදාගන්න:
   - Database Access → Add New Database User
   - Username සහ Password දෙන්න
   - "Add User" click කරන්න
6. Network Access allow කරන්න:
   - Network Access → Add IP Address
   - "Allow Access from Anywhere" click කරන්න (0.0.0.0/0)
   - Confirm කරන්න
7. Connection String ලබාගන්න:
   - Database → Connect
   - "Connect your application" select කරන්න
   - Python driver select කරන්න
   - Connection string copy කරන්න
   - `<password>` කොටස ඔබේ password එකෙන් replace කරන්න
8. `.env` file එකට add කරන්න:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=sinhala_sub_bot
   ```

#### Option 2: Local MongoDB

```bash
# Install MongoDB
sudo apt-get install mongodb

# Start MongoDB
sudo systemctl start mongodb

# .env file එකට add කරන්න:
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=sinhala_sub_bot
```

### 3️⃣ Channel Setup කිරීම

#### Main Channel (Files එකතු කිරීම සඳහා):

1. Telegram Channel එකක් හදාගන්න (Private හෝ Public)
2. Bot එක Admin ලෙස add කරන්න:
   - Channel → Administrators → Add Administrator
   - ඔබේ bot එක search කරන්න
   - "Post Messages" permission දෙන්න
3. Channel ID ලබාගන්න:
   - Channel එකෙන් message එකක් forward කරන්න @userinfobot වෙත
   - Channel ID copy කරන්න (උදා: -1001234567890)
4. `.env` file එකට add කරන්න:
   ```
   CHANNEL_ID=-1001234567890
   CHANNEL_USERNAME=@YourChannelUsername
   ```

#### Request Channel (Admin requests සඳහා - Optional):

1. තවත් channel එකක් හදාගන්න admins සඳහා
2. Bot එක admin කරන්න
3. Channel ID copy කරන්න
4. `.env` file එකට add කරන්න:
   ```
   REQUEST_CHANNEL_ID=-1001234567890
   ```

### 4️⃣ Admin IDs Setup කිරීම

1. @userinfobot වෙත යන්න
2. "/start" send කරන්න
3. ඔබේ User ID copy කරන්න
4. `.env` file එකට add කරන්න (multiple admins සඳහා comma භාවිතා කරන්න):
   ```
   ADMIN_IDS=123456789,987654321
   ```

### 5️⃣ Banner Images Setup කිරීම

#### Option 1: Telegraph (නොමිලේ)

1. https://telegra.ph/ වෙත යන්න
2. Top right corner එකෙ "UPLOAD" click කරන්න
3. ඔබේ images upload කරන්න
4. Image එක right click කරන්න → "Copy Image Address"
5. `.env` file එකට add කරන්න:
   ```
   BANNER_START=https://telegra.ph/file/xxxxx.jpg
   BANNER_HELP=https://telegra.ph/file/xxxxx.jpg
   BANNER_CONTACT=https://telegra.ph/file/xxxxx.jpg
   BANNER_SEARCH=https://telegra.ph/file/xxxxx.jpg
   ```

#### Option 2: Telegram File ID (Advanced)

1. ඔබේ bot එකට image එකක් send කරන්න
2. Bot logs වලින් file_id copy කරන්න
3. `.env` file එකට add කරන්න

### 6️⃣ Contact Information Setup කිරීම

```env
DEVELOPER_NAME=Sadesha Hansana
OWNER_NAME=Sadisa Harshana
DEVELOPER_LINK=https://t.me/YourDeveloperUsername
OWNER_LINK=https://t.me/YourOwnerUsername
OWNER_WHATSAPP=https://wa.me/94701234567
```

### 7️⃣ සම්පූර්ණ .env File උදාහරණය

```env
# Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=YourBotUsername

# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=sinhala_sub_bot

# Admin Configuration
ADMIN_IDS=123456789,987654321

# Channel Configuration
CHANNEL_ID=-1001234567890
CHANNEL_USERNAME=@YourChannel
REQUEST_CHANNEL_ID=-1001234567890

# Contact Information
DEVELOPER_NAME=Sadesha Hansana
OWNER_NAME=Sadisa Harshana
DEVELOPER_LINK=https://t.me/YourDeveloper
OWNER_LINK=https://t.me/YourOwner
OWNER_WHATSAPP=https://wa.me/94701234567

# Menu Banner Images
BANNER_START=https://telegra.ph/file/xxxxx.jpg
BANNER_HELP=https://telegra.ph/file/xxxxx.jpg
BANNER_CONTACT=https://telegra.ph/file/xxxxx.jpg
BANNER_SEARCH=https://telegra.ph/file/xxxxx.jpg
```

### 8️⃣ Dependencies Install කිරීම

```bash
pip install -r requirements.txt --break-system-packages
```

### 9️⃣ Database Test කිරීම

Bot එක run කරන්න කලින් database එක test කරන්න:

```bash
python test_database.py
```

මෙය:
- Database connection test කරනවා
- Files count show කරනවා
- Sample files show කරනවා

### 🔟 Bot එක Run කිරීම

```bash
python bot.py
```

දැන් bot එක Telegram එකේ භාවිතා කරන්න!

## 🔍 Files එකතු කරන්නේ කෙසේද?

### Auto Indexing (Recommended):

1. Bot එක ඔබේ channel එකට admin කරන්න
2. Channel එකට files post කරන්න
3. Bot එක automatically files index කරනවා
4. Users හට search කරන්න පුළුවන්

### Files Post කරන විට:

- Document files (.mkv, .mp4, .srt, .zip)
- Videos
- Audio files
- Photos

Bot එක සියල්ල automatically detect කරලා database එකට save කරනවා!

## 🐛 Common Issues & Solutions

### Issue 1: Bot එක start වෙන්නේ නැ

**විසඳුම:**
- BOT_TOKEN නිවැරදිද පරීක්ෂා කරන්න
- MongoDB URI වලංගුද පරීක්ෂා කරන්න
- `python test_database.py` run කරන්න

### Issue 2: Search වැඩ කරන්නේ නැ

**විසඳුම:**
- Database එකේ files තියෙනවාද පරීක්ෂා කරන්න
- Channel එකට bot එක admin කර ඇත්ද පරීක්ෂා කරන්න
- Files channel එකට post කර ඇත්ද පරීක්ෂා කරන්න

### Issue 3: Images show වෙන්නේ නැ

**විසඨුම:**
- Telegraph URLs නිවැරදිද පරීක්ෂා කරන්න
- Images publicly accessible ද පරීක්ෂා කරන්න
- URLs .env file එකේ නිවැරදිව ඇතුලත් කර ඇත්ද පරීක්ෂා කරන්න

### Issue 4: Ban/Unban වැඩ කරන්නේ නැ

**විසඳුම:**
- ඔබ admin ද පරීක්ෂා කරන්න (ADMIN_IDS)
- User ID නිවැරදිද පරීක්ෂා කරන්න
- `/ban 123456789` හෝ `/ban @username` භාවිතා කරන්න

### Issue 5: Broadcast වැඩ කරන්නේ නැ

**විසඳුම:**
- ඔබ admin ද පරීක්ෂා කරන්න
- Database එකේ users තියෙනවාද පරීක්ෂා කරන්න
- Send button click කරන්න confirmation එකෙන් පසු

## 📱 Deployment Options

### Option 1: Local Machine / VPS

```bash
# Screen භාවිතා කරන්න
screen -S sinhalasub
python bot.py

# Detach: Ctrl+A, D
# Re-attach: screen -r sinhalasub
```

### Option 2: Heroku

```bash
# Heroku CLI install කරන්න
heroku login
heroku create your-bot-name

# Environment variables set කරන්න
heroku config:set BOT_TOKEN=your_token
heroku config:set MONGODB_URI=your_uri
heroku config:set ADMIN_IDS=123456789

# Deploy කරන්න
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### Option 3: Railway

1. https://railway.app වෙත යන්න
2. GitHub repository connect කරන්න
3. Environment variables add කරන්න
4. Deploy button click කරන්න

### Option 4: PythonAnywhere

1. https://www.pythonanywhere.com account එකක් හදාගන්න
2. Files upload කරන්න
3. Virtual environment හදාගන්න
4. Dependencies install කරන්න
5. Always-on task එකක් සකස් කරන්න

## ✅ Verification Checklist

Setup කිරීමෙන් පසු මේවා පරීක්ෂා කරන්න:

- [ ] Bot එක start වේද?
- [ ] /start command එක වැඩ කරයිද?
- [ ] /help command එක වැඩ කරයිද?
- [ ] /contact command එක වැඩ කරයිද?
- [ ] Images show වේද menus වලදි?
- [ ] Files channel එකේ තියෙනවාද?
- [ ] Search වැඩ කරයිද?
- [ ] Pagination buttons වැඩ කරයිද?
- [ ] File download වේද?
- [ ] File caption නිවැරදිද?
- [ ] Request system වැඩ කරයිද?
- [ ] Ban/Unban වැඩ කරයිද? (Admin)
- [ ] Broadcast වැඩ කරයිද? (Admin)

සියල්ල ✅ නම් bot එක සම්පූර්ණයෙන් වැඩ කරයි! 🎉

## 📞 සහාය අවශ්‍ය නම්

ගැටළු තිබේ නම්:
1. README.md file එක කියවන්න
2. FEATURES.md file එක කියවන්න
3. Bot logs පරීක්ෂා කරන්න
4. test_database.py run කරන්න
5. Developer/Owner සම්බන්ධ කරගන්න

---

**සුභ පැතුම්! ඔබේ Sinhala Subtitle Bot එක භාවිතා කරන්න!** 🎬🇱🇰
