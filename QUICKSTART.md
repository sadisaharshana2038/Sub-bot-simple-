# ⚡ QUICK START - 5 Minutes Setup

සරලම විදියට bot එක run කරන්න!

## Step 1: Get Bot Token (1 min)

1. Telegram open කරන්න
2. Search: `@BotFather`
3. Send: `/newbot`
4. නම දෙන්න: `My Subtitle Bot`
5. Username: `my_sub_bot` (must end with `bot`)
6. **Token save කරන්න!**

## Step 2: Get MongoDB (2 min)

1. Go to: https://mongodb.com/cloud/atlas
2. Sign up FREE
3. Create FREE Cluster (M0)
4. Create User:
   - Username: `botuser`
   - Password: `YourPassword123`
5. Network Access:
   - Click "Add IP"
   - Select "Allow from Anywhere" → Confirm
6. Get Connection String:
   - Click "Connect"
   - Choose "Connect your application"
   - Copy the string
   - Replace `<password>` with your password

**Example:**
```
mongodb+srv://botuser:YourPassword123@cluster0.xxxxx.mongodb.net/
```

## Step 3: Configure (1 min)

1. Copy `.env.example` → `.env`

2. Edit `.env`:

```env
BOT_TOKEN=123456:ABC-your-token-here
MONGODB_URI=mongodb+srv://botuser:pass@cluster.mongodb.net/
ADMIN_IDS=123456789
```

**Get your Telegram ID:**
- Message `@userinfobot` on Telegram
- Copy the number

## Step 4: Run (1 min)

```bash
pip install -r requirements.txt
python setup.py
python bot.py
```

**Done!** 🎉

Test: Open bot in Telegram → Send `/start`

---

## Image Setup (Optional)

### Quick Method: Telegraph

1. Go to: https://telegra.ph
2. Upload your images
3. Copy URLs
4. Edit `bot.py`:

```python
IMAGES = {
    'welcome': 'https://telegra.ph/file/your-image.jpg',
    'loading': 'https://telegra.ph/file/loading.gif',
    # ...
}
```

---

## Add First Series

1. Start bot: `/admin`
2. Send: `/addseries`
3. Send:

```
series_id: test_series
title_en: Test Series
title_si: පරීක්ෂණ කතා මාලාව
description_en: This is a test
description_si: මෙය පරීක්ෂණයකි
category: Drama
rating: 8.5
```

Done! Now `/browse` to see it!

---

## Add First Episode

1. Upload subtitle file to bot
2. Copy file_id from log
3. Send: `/addepisode`
4. Send:

```
episode_id: test_ep1
series_id: test_series
season: 1
episode: 1
title: Episode 1
file_id: BAACAgIAAxkBAAI... (paste here)
```

Done! Users can now download!

---

## Deploy to Heroku (Free 24/7)

```bash
# Install Heroku CLI from:
# https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create my-sub-bot
heroku config:set BOT_TOKEN=your_token
heroku config:set MONGODB_URI=your_mongodb
heroku config:set ADMIN_IDS=your_id

git init
git add .
git commit -m "first"
git push heroku main
heroku ps:scale worker=1
```

**Bot is now live 24/7!** 🚀

---

## Troubleshooting

**Bot not starting?**
- Check `.env` file
- Verify BOT_TOKEN
- Test: `python bot.py`

**Database error?**
- Check MONGODB_URI
- Verify password in connection string
- Check IP whitelist (0.0.0.0/0)

**No response?**
- Check bot is running
- Try `/start` again
- Check logs

---

## Next Steps

✅ Test all features
✅ Add more series
✅ Upload subtitle files
✅ Promote your bot
✅ Get users!

**Need help?** Check README.md for full guide!

**සුභ පැතුම්! Good luck!** 🇱🇰
