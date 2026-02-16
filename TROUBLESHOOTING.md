# 🔧 TROUBLESHOOTING GUIDE - ගැටළු විසඳුම්

## 🔍 Search වැඩ නොකරන්නේ නම්

### ප්‍රධාන හේතු:

1. **Database එකේ files නැත**
   ```bash
   python test_database.py
   ```
   Files count 0 නම්:
   - Bot එක channel එකට admin කර ඇත්ද පරීක්ෂා කරන්න
   - Channel එකට files post කරන්න
   - Bot එක restart කරන්න

2. **Text Search Index නැත**
   - Bot එක පළමුවරට run වෙද්දි automatically index හදනවා
   - නැත්නම් manually හදන්න:
   ```python
   # MongoDB shell එකේ:
   db.files.createIndex({ "file_name": "text", "caption": "text" })
   ```

3. **Search Query වැරදියි**
   - අවම වශයෙන් අකුරු 2ක් තිබිය යුතුයි
   - ඉංග්‍රීසි නම් භාවිතා කරන්න
   - Spelling නිවැරදි කරන්න

### විසඳුම:

```python
# bot.py file එකේ message_handler function එක හරියටම වැඩ කරනවා
# Error message එකක් එනවා නම්:

# 1. Database connection පරීක්ෂා කරන්න
python test_database.py

# 2. Bot logs බලන්න
# Terminal එකේ error messages show වෙයි

# 3. Files manually add කරන්න test සඳහා
# Channel එකට files post කරන්න
```

## 🚫 Ban/Unban වැඩ නොකරන්නේ නම්

### හේතු:

1. **Admin නොවේ**
   - ADMIN_IDS එකේ ඔබේ ID තිබේද පරීක්ෂා කරන්න
   - @userinfobot භාවිතයෙන් ID verify කරන්න

2. **Command syntax වැරදියි**
   ```
   ✅ නිවැරදි:
   /ban 123456789 Spam
   /ban @username Abuse
   /unban 123456789
   /unban @username
   
   ❌ වැරදි:
   /ban 123456789Spam  (space නැත)
   /ban username       (@ sign නැත)
   ```

3. **User database එකේ නැත**
   - User එක bot එක use කර තිබිය යුතුයි
   - /start command එක use කර තිබිය යුතුයි

### විසඳුම:

```bash
# 1. Admin ද verify කරන්න
# Bot එකට /stats command එක send කරන්න
# "Admin Status: Active" show වෙනවාද බලන්න

# 2. Username search එක fail වෙනවා නම්:
# User ID භාවිතා කරන්න instead

# 3. Database එකේ ban collection පරීක්ෂා කරන්න
```

## 📢 Broadcast වැඩ නොකරන්නේ නම්

### හේතු:

1. **Admin නොවේ**
2. **Database එකේ users නැත**
3. **Confirmation buttons click කරලා නැත**

### විසඳුම:

```python
# 1. Admin verify කරන්න
# ADMIN_IDS එකේ ඔබේ ID ඇතුලත් කරන්න

# 2. Users count පරීක්ෂා කරන්න
python test_database.py

# 3. Broadcast flow:
/broadcast → Message send කරන්න → "Send" button click කරන්න

# 4. Forward messages වැඩ නොකරන්නේ නම්:
# Bot එකට "Copy" permission තිබිය යුතුයි
```

## 🖼️ Images Show නොවන්නේ නම්

### හේතු:

1. **Telegraph URLs වැරදියි**
2. **Images publicly accessible නැත**
3. **.env file එකේ URLs නැත**

### විසඳුම:

```bash
# 1. Telegraph URLs verify කරන්න
# Browser එකේ URL එක open කරලා බලන්න

# 2. .env file check කරන්න
cat .env | grep BANNER

# Output:
# BANNER_START=https://telegra.ph/file/xxxxx.jpg
# BANNER_HELP=https://telegra.ph/file/xxxxx.jpg
# BANNER_CONTACT=https://telegra.ph/file/xxxxx.jpg
# BANNER_SEARCH=https://telegra.ph/file/xxxxx.jpg

# 3. URLs නැත්නම්:
# bot.py එකේ default URLs තිබේ
# Menu text only show වේ (images නැතිව)
```

## ⬅️➡️ Pagination වැඩ නොකරන්නේ නම්

### හේතු:

1. **Callback handler error**
2. **Context data lost**
3. **Button callback data වැරදියි**

### විසඳුම:

මෙම bot version එකේ pagination සම්පූර්ණයෙන් වැඩ කරයි!

```python
# Pagination buttons:
# ⬅️ පෙර - Previous page
# 📄 1/5 - Current page (info only)
# ඊළඟ ➡️ - Next page

# Error එකක් එනවා නම්:
# 1. Bot restart කරන්න
# 2. නැවත search කරන්න
# 3. Logs බලන්න terminal එකේ
```

## 📁 Files Download නොවන්නේ නම්

### හේතු:

1. **File ID වලංගු නැත**
2. **File type අනාවරණය නොවේ**
3. **Bot එකට file access නැත**

### විසඳුම:

```python
# 1. File database එකේ ද verify කරන්න
python test_database.py

# 2. File type පරීක්ෂා කරන්න
# Supported: document, video, audio, photo

# 3. File ID expired වෙලාද බලන්න
# Channel post delete කරලා නැතිද බලන්න

# 4. Caption error නම්:
# bot.py එකේ create_file_caption function එක පරීක්ෂා කරන්න
```

## 📝 Request System වැඩ නොකරන්නේ නම්

### හේතු:

1. **Conversation state lost**
2. **REQUEST_CHANNEL_ID වැරදියි**
3. **Admin channel එකට bot එක admin නැත**

### විසඳුම:

```bash
# 1. Request flow පරීක්ෂා කරන්න
/request → නම send කරන්න → වසර send කරන්න → Done!

# 2. Admin notification නැත්නම්:
# REQUEST_CHANNEL_ID set කර ඇත්ද බලන්න
# Bot එක admin කර ඇත්ද channel එකට බලන්න

# 3. /cancel command භාවිතා කරන්න අවලංගු කරන්න
```

## 🔐 Database Connection Issues

### MongoDB Atlas:

```bash
# Error: "Authentication failed"
# විසඳුම:
# - Username සහ password නිවැරදි කරන්න
# - Connection string එකේ <password> replace කරන්න

# Error: "IP not whitelisted"
# විසඳුම:
# - Network Access → Add IP Address
# - 0.0.0.0/0 allow කරන්න (anywhere)

# Error: "Connection timeout"
# විසඳුම:
# - Internet connection පරීක්ෂා කරන්න
# - Firewall settings පරීක්ෂා කරන්න
```

### Local MongoDB:

```bash
# Error: "Connection refused"
# විසඳුම:
sudo systemctl start mongodb
sudo systemctl status mongodb

# MongoDB running ද verify කරන්න:
ps aux | grep mongo
```

## ⚙️ Bot Crashes / Stops

### හේතු:

1. **Error handling නැත**
2. **Memory overflow**
3. **API rate limit**

### විසඳුම:

```bash
# 1. Logs පරීක්ෂා කරන්න
# Terminal output බලන්න

# 2. Bot restart කරන්න
# Screen භාවිතා කරන්න:
screen -S sinhalasub
python bot.py
# Ctrl+A, D to detach

# 3. Memory issues නම්:
# Restart bot එක periodically
# Cron job එකක් setup කරන්න

# 4. Rate limit issues නම්:
# Broadcast වලදි users limit කරන්න
# Delays add කරන්න
```

## 🔄 Auto-Indexing වැඩ නොකරන්නේ නම්

### හේතු:

1. **Bot එක channel admin නැත**
2. **Bot එකට permissions නැත**
3. **Channel ID වැරදියි**

### විසඳුම:

```bash
# 1. Bot එක admin කරන්න channel එකට
# Channel → Administrators → Add Administrator
# "Post Messages" permission දෙන්න

# 2. Channel ID verify කරන්න
# Channel එකෙන් message forward කරන්න @userinfobot වෙත
# ID copy කරන්න (-100 prefix එක්ක)

# 3. .env file update කරන්න
CHANNEL_ID=-1001234567890
CHANNEL_USERNAME=@YourChannel

# 4. Bot restart කරන්න
# Files post කරන්න channel එකට
# Bot logs බලන්න "✅ Indexed:" messages
```

## 🧪 Testing Commands

### Database Test:
```bash
python test_database.py
```

### Bot Test:
```
/start - Bot running ද බලන්න
/help - Help working ද බලන්න
/stats - Stats show වේද බලන්න
/contact - Contact working ද බලන්න
```

### Admin Test:
```
/ban @testuser Test - Ban working ද
/unban @testuser - Unban working ද
/broadcast - Broadcast working ද
/deleteduplicates - Duplicates delete වේද
```

### Search Test:
```
අඩවි තුළ movie නමක් ටයිප් කරන්න
Buttons show වේද බලන්න
Pagination වැඩ කරයිද බලන්න
File download වේද බලන්න
Caption නිවැරදිද බලන්න
```

## 📊 Common Error Messages & Solutions

### "❌ දෝෂයක් සිදුවිය"
- Generic error
- Logs පරීක්ෂා කරන්න
- Bot restart කරන්න

### "❌ සෙවීමේදී දෝෂයක්!"
- Database connection පරීක්ෂා කරන්න
- Files තිබේද බලන්න
- Search index තිබේද බලන්න

### "❌ File not found!"
- File database එකේ නැත
- File ID expired
- File deleted from channel

### "❌ ඔබව තහනම් කර ඇත!"
- User banned
- Admin contact කරන්න
- Unban request කරන්න

### "❌ No permission!"
- Admin only command
- ADMIN_IDS එකේ ID add කරන්න

## 🆘 Emergency Recovery

Bot එක සම්පූර්ණයෙන් වැඩ නොකරන්නේ නම්:

```bash
# 1. Clean restart
pkill -f bot.py
rm -rf __pycache__
python bot.py

# 2. Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt --break-system-packages

# 3. Database reset (careful!)
# MongoDB Atlas එකේ:
# Database → Collections → Drop collection

# 4. Fresh setup
# .env file නැවත හදන්න
# All configurations verify කරන්න
# Bot නැවත run කරන්න
```

## 💡 Best Practices

1. **Always keep backups**
   - .env file
   - Database exports
   - Bot logs

2. **Monitor regularly**
   - Bot status
   - Database size
   - Error logs

3. **Update regularly**
   - Dependencies
   - Bot code
   - MongoDB

4. **Test before production**
   - Local testing
   - Test channel
   - Test users

5. **Use logging**
   - Keep logs
   - Monitor errors
   - Track usage

---

**තවත් ගැටළු තිබේද? Developer/Owner contact කරන්න!** 📞
